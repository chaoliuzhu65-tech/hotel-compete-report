# hotel-compete-report Skill v3.0

> 酒店竞品价格监测 + 行业扩展 + 调价建议
> 高德地图POI + 飞猪价格API + amap-sdk官方SDK

---

## 四大核心模块

| 模块 | 路径 | 功能 |
|------|------|------|
| **多维竞品评分** | `core/competitor_filter.py` | 距离×星级×品牌×价格四维评分 |
| **amap-sdk封装** | `core/amap_client.py` | 官方Python SDK（替代CLI）|
| **行业扩展检索** | `industry_search/multi_industry.py` | 酒店/餐饮/零售/银行/出行全链 |
| **调价算法** | `algorithm/pricing_advisor.py` | AI调价建议（独立Skill）|

---

## 快速使用

### 1. 安装依赖

```bash
pip install amap-sdk pandas openai
export AMAP_MAPS_API_KEY="你的Key"
```

### 2. 多维竞品评分

```python
from core.competitor_filter import HotelPOI, filter_competitors, CompetitorScore

target = HotelPOI(
    name="天津瑞湾开元名都",
    location="117.745689,39.021567",
    star="高档型",
    brand="开元",
    price=443
)
candidates = [
    HotelPOI(name="天津于家堡洲际", location="117.701234,39.012345",
             star="五星级", brand="洲际", price=916, distance_km=4.2),
    HotelPOI(name="天津泰达万豪", location="117.723456,39.034567",
             star="五星级", brand="万豪", price=812, distance_km=2.8),
]
scores = filter_competitors(candidates, target, base_price=443, max_distance_km=5.0)
for s in scores:
    print(f"✅ {s.hotel.name} | 总分:{s.total_score}")
```

### 3. 行业扩展检索

```python
from industry_search.multi_industry import MultiIndustrySearcher

searcher = MultiIndustrySearcher(api_key="你的Key")
searcher.set_hotel_location("天津瑞湾开元名都", (117.745689, 39.021567))
report = searcher.generate_report(
    categories=["住宿", "餐饮", "出行", "购物", "金融"],
    radius_km=5
)
searcher.print_report(report)
```

**输出示例：**
```
🏨 天津瑞湾开元名都 | 半径5km出行全链报告
🏨 住宿（竞品酒店监测）  总数：38家 | 3km内：32家 | 完善度：100.0/100
🍽️ 餐饮（目的地餐饮配套）总数：49家 | 3km内：37家 | 完善度：80.0/100
✈️ 出行（交通便利性评估）总数：23家 | 3km内：22家 | 完善度：90.0/100
📊 综合配套评分：319/100
```

### 4. AI调价建议

```python
from algorithm.pricing_advisor import PricingAdvisor, CompetitorData, DemandLevel

competitors = [
    CompetitorData("于家堡洲际", base_price=916, holiday_price=1397, star="五星级"),
    CompetitorData("滨海皇冠假日", base_price=848, holiday_price=1349, star="五星级"),
    CompetitorData("万丽泰达", base_price=721, holiday_price=1108, star="五星级"),
    CompetitorData("泰达万豪", base_price=673, holiday_price=1026, star="五星级"),
]
advisor = PricingAdvisor(
    base_price=443,
    competitors=competitors,
    demand_level=DemandLevel.HIGH,
    target_date="2026-05-01"
)
rec = advisor.analyze()
advisor.print_recommendation(rec)
```

**输出示例：**
```
✅ 推荐策略：AGGRESSIVE
💰 推荐价格：¥722
📈 推荐涨幅：+63.0%
🎯 置信度：95%
💡 备选方案：
     conservative ¥640（+44.6%）
     standard     ¥697（+57.5%）
   ⭐ aggressive  ¥722（+63.0%）
```

### 5. 飞猪价格采集

```bash
export FLIGGY_KEY="你的飞猪API Key"
python scripts/build_compete_report.py \
  --hotel "天津瑞湾开元名都" \
  --target-date 2026-05-01 \
  --base-price 443
```

---

## 多维评分体系

```
竞品得分 = 距离分(30%) × 星级分(30%) × 品牌分(20%) × 价格分(20%)

距离分：≤1km=100分, ≤3km=80分, ≤5km=60分, >5km=0分
星级分：同档=100, 相邻=60, 相差2档=20, 未知=50
品牌分：同档次=100, 相邻=70, 其他=50
价格分：±30%重叠=100, ±50%=60, >50%=20
```

---

## 调价算法核心逻辑

```
Step 1: 价格弹性分析
  → 计算竞品涨幅变异系数（CV）
  → CV>0.5=高弹性（竞争激烈），CV<0.2=低弹性（走势趋同）

Step 2: 竞争定位指数（CPI）
  → CPI = 目标酒店平日价 / 竞品平均假日价 × 100
  → CPI>120=高端定位，90-120=中高端，70-90=中端性价比

Step 3: 需求强度判断
  → HIGH（节假日）→ 选激进策略
  → MEDIUM（周末）→ 选标准策略
  → LOW（工作日）→ 选保守策略

Step 4: 三档定价输出
  → 保守：中位数涨幅×0.85
  → 标准：弹性调整后中位数
  → 激进：中位数涨幅×1.20
```

---

## 定时任务（每日监测）

```bash
# 每日08:00自动执行
0 8 * * * cd /root/.openclaw/workspace/hotel-compete-report && \
  python3 scripts/build_compete_report.py \
    --hotel "天津瑞湾开元名都" \
    --target-date $(date -d+1day +\%Y-\%m-\%d) \
    --base-price 443 \
    --notify
```

---

## GitHub

- 仓库：https://github.com/chaoliuzhu65-tech/hotel-compete-report
- v3.0发布：https://github.com/chaoliuzhu65-tech/hotel-compete-report/releases/tag/v1.0.0

## 依赖

```
amap-sdk>=0.1.0
pandas
requests
openai（用于AI调价建议）
```
