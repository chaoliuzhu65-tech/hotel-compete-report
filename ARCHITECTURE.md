# hotel-compete-report v3.0 架构设计

## 四大核心模块

```
hotel-compete-report-v3/
├── core/                           # 核心引擎
│   ├── __init__.py
│   ├── competitor_filter.py        # 多维竞品评分（距离×星级×品牌×价格）
│   ├── amap_client.py              # amap-sdk 官方SDK封装（替代CLI）
│   ├── fliggy_client.py           # 飞猪开放平台API封装
│   └── data_cache.py               # 竞品数据库（内置+实时）
│
├── daily_report/                   # 每日实时监测日报
│   ├── __init__.py
│   ├── daily_monitor.py            # 定时采集+报告生成
│   └── templates/
│       └── daily_report_template.md
│
├── industry_search/                # 行业扩展检索
│   ├── __init__.py
│   └── multi_industry.py           # 酒店/餐饮/零售/银行/出行全链
│
├── algorithm/                      # 调价算法（独立Skill）
│   ├── __init__.py
│   ├── pricing_advisor.py         # AI调价建议引擎
│   ├── elasticity.py               # 价格弹性分析
│   ├── competitive_position.py     # 竞争定位分析
│   └── demand_forecast.py          # 需求预测
│
└── skills/
    ├── hotel-compete-report/       # 主Skill（竞品价格监测）
    └── pricing-advisor/            # 独立Skill（调价算法）
```

## 多维竞品评分体系

```
竞品得分 = 距离分(30%) × 星级分(30%) × 品牌分(20%) × 价格分(20%)

距离分：≤1km=100分, ≤3km=80分, ≤5km=60分, >5km=0分
星级分：同星级=100分, 相邻星级=60分, 相差2档=20分
品牌分：同集团=100分, 同档次=80分, 其他=50分
价格分：价格带重叠=100分, 相邻带=60分, 相差大=20分
```

## 每日监测流程

```
08:00 定时触发
  → 读取飞猪今日价格（目标酒店+竞品）
  → 高德POI二次验证（距离+星级）
  → 多维评分筛选有效竞品
  → 生成Markdown日报
  → 推送飞书群/私信用户
```

## 行业扩展分类（高德POI）

| 行业 | 高德POI类型 | 用途 |
|------|------------|------|
| 住宿 | 宾馆酒店/五星级等 | 竞品价格监测 |
| 餐饮 | 餐饮服务/中餐/西餐 | 出行全链分析 |
| 购物 | 商场/超市/专卖店 | 目的地吸引力 |
| 金融 | 银行/ATM | 商旅客户配套 |
| 出行 | 机场/火车站/地铁 | 交通便利性评估 |

## 调价算法Skill（独立）

```bash
# 触发方式
/skiving <竞品数据JSON>

# 算法输入
{
  "target_hotel": "天津瑞湾开元名都",
  "base_price": 443,
  "competitors": [{"name": "...", "base": 333, "holiday": 412, "rate": 23.7, ...}],
  "target_date": "2026-05-01",
  "demand_level": "high"  # high/medium/low（AI判断）
}

# 算法输出
{
  "recommended_price": 636,
  "rate": 43.6,
  "strategy": "standard",
  "reasoning": "中位数涨幅43.8%，略高于竞品平均...",
  "alternatives": [{"price": 607, "strategy": "conservative"}, ...]
}
```
