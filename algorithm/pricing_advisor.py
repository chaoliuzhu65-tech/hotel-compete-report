#!/usr/bin/env python3
"""
pricing_advisor.py - AI调价建议引擎 v1.0
独立Skill：竞品价格数据 → 智能调价建议

不仅仅依赖"双重校准"，而是综合以下维度：
1. 价格弹性分析（Elasticity Analysis）
2. 竞争定位指数（Competitive Position Index）
3. 需求强度信号（Demand Signals）
4. 收益管理最佳实践（RMS Best Practices）

独立触发命令：
/price_advise <竞品数据JSON>
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
import statistics
import math


# ── 数据模型 ─────────────────────────────────────────────

class DemandLevel(Enum):
    HIGH = "high"      # 节假日/旺季
    MEDIUM = "medium"  # 平日周末
    LOW = "low"        # 淡季/工作日


class PricingStrategy(Enum):
    CONSERVATIVE = "conservative"  # 保守（保出租率）
    STANDARD = "standard"          # 标准（平衡）
    AGGRESSIVE = "aggressive"      # 激进（追收益）
    PREMIUM = "premium"            # 溢价（供不应求）


@dataclass
class CompetitorData:
    """竞品数据结构"""
    name: str
    base_price: float       # 平日价
    holiday_price: float    # 目标日价格
    star: str = ""          # 星级
    brand: str = ""         # 品牌
    distance_km: float = 0  # 距离km
    occupancy_hint: str = "" # 满房/high/medium/low


@dataclass
class PricingRecommendation:
    """调价建议结果"""
    recommended_price: int
    strategy: PricingStrategy
    rate: float              # 涨幅%
    confidence: float        # 置信度 0-100
    reasoning: List[str]     # 分析理由
    alternatives: List[Dict] # 备选方案
    elasticity_score: float  # 价格弹性指数
    cpi_score: float         # 竞争定位指数
    demand_level: DemandLevel


# ── 核心分析函数 ─────────────────────────────────────────

class PricingAdvisor:
    """
    AI调价建议引擎

    输入：竞品价格数据 + 目标酒店平日基准价
    输出：多策略调价建议 + 分析理由
    """

    def __init__(self, base_price: float, competitors: List[CompetitorData],
                 demand_level: DemandLevel = DemandLevel.MEDIUM,
                 target_date: str = ""):
        self.base_price = base_price
        self.competitors = competitors
        self.demand_level = demand_level
        self.target_date = target_date

    def analyze(self) -> PricingRecommendation:
        """执行综合分析，返回调价建议"""
        rates = [(c.name, c.base_price, c.holiday_price,
                  (c.holiday_price - c.base_price) / c.base_price * 100)
                 for c in self.competitors if c.base_price > 0]

        # ── Step 1：价格弹性分析 ──────────────────────────
        elasticity = self._calc_elasticity(rates)

        # ── Step 2：竞争定位指数（CPI）─────────────────────
        cpi, self_position = self._calc_cpi()

        # ── Step 3：需求强度判断 ────────────────────────────
        demand_score = self._calc_demand_score()

        # ── Step 4：多策略定价 ─────────────────────────────
        strategies = self._generate_strategies(rates, elasticity, cpi, demand_score)

        # ── Step 5：选择最优策略 ────────────────────────────
        best = self._select_best_strategy(strategies)

        return best

    def _calc_elasticity(self, rates: List) -> Dict:
        """
        价格弹性分析
        高弹性：价格对需求影响大 → 提价要谨慎
        低弹性：价格对需求影响小 → 可以激进提价
        """
        if len(rates) < 2:
            return {"elasticity": "medium", "score": 0.5, "reason": "数据不足"}

        holiday_prices = [r[3] for r in rates]  # 涨幅列表
        std_dev = statistics.stdev(holiday_prices) if len(holiday_prices) > 1 else 0
        mean_rate = statistics.mean(holiday_prices)

        # 变异系数（CV）越大说明市场弹性越高
        cv = std_dev / abs(mean_rate) if mean_rate != 0 else 0

        if cv > 0.5:
            elasticity = "high"
            score = 0.8
            reason = f"市场竞争激烈（变异系数={cv:.2f}），价格分散"
        elif cv > 0.2:
            elasticity = "medium"
            score = 0.5
            reason = f"市场竞争稳定（变异系数={cv:.2f}）"
        else:
            elasticity = "low"
            score = 0.3
            reason = f"市场竞争趋同（变异系数={cv:.2f}），价格走势一致"

        return {"elasticity": elasticity, "score": score, "reason": reason,
                "cv": cv, "mean_rate": mean_rate}

    def _calc_cpi(self,) -> tuple:
        """
        竞争定位指数（Competitive Position Index）
        CPI > 100：价格高于竞品平均（溢价定位）
        CPI < 100：价格低于竞品平均（性价比定位）
        CPI = 100：与竞品持平
        """
        if not self.competitors:
            return (100.0, "持平")

        comp_avg = statistics.mean([c.holiday_price for c in self.competitors if c.holiday_price])
        if comp_avg == 0:
            return (100.0, "持平")

        cpi = (self.base_price / comp_avg) * 100

        if cpi > 120:
            position = "高端定位"
        elif cpi > 90:
            position = "中高端定位"
        elif cpi > 70:
            position = "中端性价比"
        else:
            position = "经济型定位"

        return (round(cpi, 1), position)

    def _calc_demand_score(self,) -> float:
        """需求强度评估（0-1）"""
        # 需求强度由demand_level决定，后续可扩展
        level_map = {DemandLevel.HIGH: 0.9, DemandLevel.MEDIUM: 0.5, DemandLevel.LOW: 0.2}
        return level_map.get(self.demand_level, 0.5)

    def _generate_strategies(self, rates: List, elasticity: Dict,
                              cpi: float, demand_score: float) -> Dict:
        """
        生成三档调价策略
        """
        if not rates:
            # 无竞品数据时，使用基础涨幅
            return {
                "conservative": {"price": int(self.base_price * 1.20), "rate": 20},
                "standard": {"price": int(self.base_price * 1.30), "rate": 30},
                "aggressive": {"price": int(self.base_price * 1.40), "rate": 40},
            }

        # 使用竞品涨幅数据
        all_rates = [r[3] for r in rates]
        median_rate = statistics.median(all_rates)

        # 去异常值（超过2倍标准差）
        if len(all_rates) >= 3:
            mean_r = statistics.mean(all_rates)
            std_r = statistics.stdev(all_rates)
            filtered = [r for r in all_rates if abs(r - mean_r) <= 2 * std_r]
            if filtered:
                median_rate = statistics.median(filtered)

        # 弹性调整：低弹性可激进，高弹性要保守
        elast_score = elasticity.get("score", 0.5)
        demand_score = demand_score

        # 综合调整系数
        adj_factor = 1 + (1 - elast_score) * 0.15 * demand_score

        conservative_rate = median_rate * 0.85  # 保守：低于中位数15%
        standard_rate = median_rate * adj_factor  # 标准：弹性调整后
        aggressive_rate = median_rate * 1.20     # 激进：中位数+20%

        return {
            "conservative": {
                "price": int(self.base_price * (1 + conservative_rate / 100)),
                "rate": round(conservative_rate, 1)
            },
            "standard": {
                "price": int(self.base_price * (1 + standard_rate / 100)),
                "rate": round(standard_rate, 1)
            },
            "aggressive": {
                "price": int(self.base_price * (1 + aggressive_rate / 100)),
                "rate": round(aggressive_rate, 1)
            },
        }

    def _select_best_strategy(self, strategies: Dict) -> PricingRecommendation:
        """选择最优策略并构建完整建议"""
        # 默认选择标准策略
        std = strategies.get("standard", strategies.get("conservative"))

        # 考虑需求强度：HIGH需求选激进，LOW需求选保守
        if self.demand_level == DemandLevel.HIGH:
            std = strategies.get("aggressive", std)
        elif self.demand_level == DemandLevel.LOW:
            std = strategies.get("conservative", std)

        strategy_key = [k for k, v in strategies.items() if v["price"] == std["price"]]
        strategy_key = strategy_key[0] if strategy_key else "standard"

        # 计算置信度（基于竞品数量和数据质量）
        n = len(self.competitors)
        if n >= 5:
            confidence = min(95, 70 + n * 5)
        elif n >= 3:
            confidence = min(80, 60 + n * 5)
        else:
            confidence = 50

        elasticity = self._calc_elasticity([(c.name, c.base_price, c.holiday_price,
                        (c.holiday_price - c.base_price) / c.base_price * 100)
                       for c in self.competitors if c.base_price > 0])

        cpi, position = self._calc_cpi()

        reasoning = [
            f"基于{len(self.competitors)}家竞品数据分析",
            f"竞品涨幅中位数：{elasticity.get('mean_rate', 0):.1f}%",
            f"市场弹性：{elasticity.get('elasticity', 'medium')}（{elasticity.get('reason', '')}）",
            f"目标酒店CPI：{cpi}（{position}）",
            f"需求强度：{self.demand_level.value}",
        ]

        return PricingRecommendation(
            recommended_price=std["price"],
            strategy=PricingStrategy(strategy_key),
            rate=std["rate"],
            confidence=confidence,
            reasoning=reasoning,
            alternatives=[
                {"strategy": k, "price": v["price"], "rate": v["rate"]}
                for k, v in strategies.items()
            ],
            elasticity_score=elasticity.get("score", 0.5),
            cpi_score=cpi,
            demand_level=self.demand_level,
        )

    def print_recommendation(self, rec: PricingRecommendation) -> None:
        """打印调价建议"""
        emoji_map = {
            PricingStrategy.CONSERVATIVE: "🛡️",
            PricingStrategy.STANDARD: "⚖️",
            PricingStrategy.AGGRESSIVE: "🚀",
            PricingStrategy.PREMIUM: "💎",
        }
        e = emoji_map.get(rec.strategy, "📊")

        print(f"\n{'='*55}")
        print(f"  {e} AI调价建议报告")
        print(f"{'='*55}")
        print(f"📅 目标日期：{self.target_date or '（未指定）'}")
        print(f"🏨 目标酒店：{self.base_price}元（平日基准）")
        print(f"📊 需求强度：{rec.demand_level.value}")
        print(f"\n{'─'*55}")
        print(f"✅ 推荐策略：{rec.strategy.value.upper()}")
        print(f"💰 推荐价格：¥{rec.recommended_price}")
        print(f"📈 推荐涨幅：+{rec.rate:.1f}%")
        print(f"🎯 置信度：{rec.confidence:.0f}%")
        print(f"\n{'─'*55}")
        print(f"🔍 分析理由：")
        for r in rec.reasoning:
            print(f"   • {r}")
        print(f"\n{'─'*55}")
        print(f"💡 备选方案：")
        for alt in rec.alternatives:
            star = "⭐" if alt["strategy"] == rec.strategy.value else "  "
            print(f"   {star} {alt['strategy']:<12} ¥{alt['price']:>5}（+{alt['rate']:.1f}%）")
        print(f"\n{'='*55}\n")


# ── 快速测试 ────────────────────────────────────────────

if __name__ == "__main__":
    competitors = [
        CompetitorData("于家堡洲际", base_price=916, holiday_price=1397, star="五星级", distance_km=4.2),
        CompetitorData("滨海皇冠假日", base_price=848, holiday_price=1349, star="五星级", distance_km=5.1),
        CompetitorData("万丽泰达", base_price=721, holiday_price=1108, star="五星级", distance_km=6.3),
        CompetitorData("泰达万豪", base_price=673, holiday_price=1026, star="五星级", distance_km=3.1),
        CompetitorData("滨海一号酒店", base_price=380, holiday_price=560, star="高档型", distance_km=2.8),
    ]

    advisor = PricingAdvisor(
        base_price=443,
        competitors=competitors,
        demand_level=DemandLevel.HIGH,
        target_date="2026-05-01"
    )

    rec = advisor.analyze()
    advisor.print_recommendation(rec)
