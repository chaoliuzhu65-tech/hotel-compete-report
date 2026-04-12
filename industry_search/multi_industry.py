#!/usr/bin/env python3
"""
multi_industry.py - 出行全链行业扩展检索
基于高德POI，支持酒店/餐饮/零售/银行/出行等全行业分类检索

核心能力：
1. 按行业分类检索（住宿/餐饮/购物/金融/出行）
2. 按距离排序（半径5km内的各类设施）
3. 距目标酒店的综合距离评分
4. 生成目的地吸引力报告
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from core.amap_client import AmapClientWrapper, POIRecord, GeoPoint
import os


# ── 行业分类配置 ─────────────────────────────────────────

INDUSTRY_CATEGORIES = {
    "住宿": {
        "keywords": ["酒店", "宾馆", "旅馆", "公寓", "民宿"],
        "poi_types": "住宿服务",
        "weight": 1.0,        # 对出行决策影响权重
        "icon": "🏨",
        "description": "竞品酒店监测"
    },
    "餐饮": {
        "keywords": ["餐厅", "饭店", "酒楼", "美食", "火锅", "烧烤", "快餐"],
        "poi_types": "餐饮服务",
        "weight": 0.8,
        "icon": "🍽️",
        "description": "目的地餐饮配套"
    },
    "购物": {
        "keywords": ["商场", "购物中心", "超市", "奥特莱斯", "商业街"],
        "poi_types": "购物服务",
        "weight": 0.7,
        "icon": "🛒",
        "description": "目的地购物配套"
    },
    "金融": {
        "keywords": ["银行", "ATM", "信用社", "保险公司"],
        "poi_types": "金融保险服务",
        "weight": 0.5,
        "icon": "🏦",
        "description": "商旅客户配套"
    },
    "出行": {
        "keywords": ["地铁站", "公交站", "火车站", "机场", "码头", "长途客运"],
        "poi_types": "交通设施",
        "weight": 0.9,
        "icon": "✈️",
        "description": "交通便利性评估"
    },
    "医疗": {
        "keywords": ["医院", "诊所", "药店", "药房"],
        "poi_types": "医疗保健服务",
        "weight": 0.6,
        "icon": "🏥",
        "description": "应急医疗配套"
    },
    "景区": {
        "keywords": ["公园", "景区", "博物馆", "展览馆", "纪念馆"],
        "poi_types": "风景名胜",
        "weight": 0.8,
        "icon": "🏞️",
        "description": "目的地旅游资源"
    },
}


@dataclass
class IndustryReport:
    """行业检索报告"""
    category: str
    icon: str
    description: str
    total_count: int
    nearby_count: int      # 3km内数量
    nearest: Optional[POIRecord]
    all_pois: List[POIRecord]
    coverage_score: float  # 0-100 配套完善度


class MultiIndustrySearcher:
    """
    多行业出行全链检索器

    使用方式：
        searcher = MultiIndustrySearcher(api_key="你的Key")
        searcher.set_hotel_location("天津瑞湾开元名都", (117.745689, 39.021567))
        report = searcher.generate_report(categories=["住宿","餐饮","出行"], radius_km=5)
    """

    def __init__(self, api_key: Optional[str] = None):
        self.amap = AmapClientWrapper(api_key=api_key)
        self.hotel_name: str = ""
        self.hotel_location: Tuple[float, float] = (0.0, 0.0)

    def set_hotel_location(self, name: str, location: Tuple[float, float]):
        """设置目标酒店位置"""
        self.hotel_name = name
        self.hotel_location = location

    def search_category(
        self,
        category: str,
        radius_km: float = 5.0,
        max_results: int = 20,
    ) -> IndustryReport:
        """
        搜索单个行业分类

        Args:
            category: 行业分类（如"住宿"/"餐饮"/"出行"）
            radius_km: 搜索半径（km）
            max_results: 最大返回数量

        Returns:
            IndustryReport
        """
        cfg = INDUSTRY_CATEGORIES.get(category, {})
        keywords = cfg.get("keywords", [category])

        # 多关键词合并搜索
        all_pois: List[POIRecord] = []
        seen_names = set()

        for kw in keywords[:3]:  # 最多3个关键词
            pois = self.amap.poi_around(
                keywords=kw,
                location=self.hotel_location,
                radius_km=radius_km,
                page_size=max_results,
            )
            for p in pois:
                if p.name not in seen_names:
                    seen_names.add(p.name)
                    # 批量计算距离
                    d = self._point_distance(p.lon, p.lat)
                    p.distance_km = d
                    all_pois.append(p)

        # 按距离排序
        all_pois.sort(key=lambda x: x.distance_km or 999)

        # 统计3km内数量
        nearby = [p for p in all_pois if (p.distance_km or 999) <= 3.0]

        # 计算配套完善度
        weight = cfg.get("weight", 0.5)
        base_score = min(len(all_pois) / 10, 1.0) * 50  # 数量得分（上限50）
        nearby_score = min(len(nearby) / 5, 1.0) * 50  # 3km内得分（上限50）
        coverage_score = round((base_score + nearby_score) * weight, 1)

        return IndustryReport(
            category=category,
            icon=cfg.get("icon", "🏢"),
            description=cfg.get("description", ""),
            total_count=len(all_pois),
            nearby_count=len(nearby),
            nearest=all_pois[0] if all_pois else None,
            all_pois=all_pois[:max_results],
            coverage_score=coverage_score,
        )

    def generate_report(
        self,
        categories: Optional[List[str]] = None,
        radius_km: float = 5.0,
    ) -> Dict:
        """
        生成多行业出行全链报告

        Returns:
            {
                "hotel": "天津瑞湾开元名都",
                "location": (117.745689, 39.021567),
                "radius_km": 5,
                "categories": {
                    "住宿": IndustryReport(...),
                    "餐饮": IndustryReport(...),
                    ...
                },
                "summary": "..."
            }
        """
        if categories is None:
            categories = list(INDUSTRY_CATEGORIES.keys())

        reports = {}
        for cat in categories:
            reports[cat] = self.search_category(cat, radius_km=radius_km)

        # 计算综合得分
        total_score = sum(r.coverage_score * INDUSTRY_CATEGORIES[cat].get("weight", 0.5)
                          for cat, r in reports.items())

        return {
            "hotel": self.hotel_name,
            "location": self.hotel_location,
            "radius_km": radius_km,
            "categories": reports,
            "comprehensive_score": round(total_score, 1),
        }

    def _point_distance(self, lon: float, lat: float) -> float:
        """计算到目标酒店的距离（km）"""
        pt = GeoPoint(lon=self.hotel_location[0], lat=self.hotel_location[1])
        other = GeoPoint(lon=lon, lat=lat)
        return round(pt.distance_to(other), 2)

    def print_report(self, report: Dict) -> None:
        """打印行业报告（人类可读格式）"""
        print(f"\n{'='*60}")
        print(f"🏨 {report['hotel']} | 半径{report['radius_km']}km出行全链报告")
        print(f"{'='*60}")

        for cat, r in report["categories"].items():
            icon = INDUSTRY_CATEGORIES.get(cat, {}).get("icon", "🏢")
            print(f"\n{icon} {cat}（{r.description}）")
            print(f"   总数：{r.total_count}家 | 3km内：{r.nearby_count}家 | 完善度：{r.coverage_score}/100")
            if r.nearest:
                d = r.nearest.distance_km
                print(f"   最近：{r.nearest.name}（{d}km）{'⭐' if d <= 1 else '✓'}")

        print(f"\n{'─'*60}")
        print(f"📊 综合配套评分：{report['comprehensive_score']:.0f}/100")
        print(f"{'='*60}\n")


# ── 快速测试 ────────────────────────────────────────────

if __name__ == "__main__":
    key = os.environ.get("AMAP_MAPS_API_KEY", "0f9da10a87fa96c564f2d3d0f459fd6f")

    searcher = MultiIndustrySearcher(api_key=key)
    searcher.set_hotel_location(
        "天津瑞湾开元名都",
        (117.745689, 39.021567)
    )

    report = searcher.generate_report(
        categories=["住宿", "餐饮", "出行", "购物", "金融"],
        radius_km=5
    )
    searcher.print_report(report)
