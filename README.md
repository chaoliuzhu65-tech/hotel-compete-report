# hotel-compete-report v3.0

> 酒店竞品价格监测 + 行业扩展检索 + AI调价建议引擎

[🏠 中文说明](SKILL.md) | [📖 English](README-en.md)

---

## 核心能力

| 能力 | 技术 | 状态 |
|------|------|------|
| 高德POI精准定位 | amap-sdk官方SDK | ✅ |
| 飞猪实时价格采集 | Fliggy API | ✅ |
| 多维竞品评分 | 距离×星级×品牌×价格四维模型 | ✅ |
| 行业扩展检索 | 酒店/餐饮/零售/银行/出行全链 | ✅ |
| AI调价建议 | 价格弹性+CPI+需求信号算法 | ✅ |
| 每日定时监测 | Cron定时任务+飞书推送 | ✅ |

---

## 快速开始

```bash
# 1. 安装
pip install amap-sdk pandas
export AMAP_MAPS_API_KEY="你的Key"

# 2. 竞品价格分析
python3 algorithm/pricing_advisor.py
# → 推荐价格：¥722（激进）/ ¥697（标准）/ ¥640（保守）

# 3. 出行全链行业扩展
python3 industry_search/multi_industry.py
# → 住宿38家 | 餐饮49家 | 出行23家 | 购物45家 | 金融37家

# 4. 多维竞品评分
python3 core/competitor_filter.py
# → 有效竞品：泰达万豪(60分)、于家堡洲际(54分)
```

---

## 核心算法

### 多维竞品评分

```
竞品得分 = 距离分(30%) × 星级分(30%) × 品牌分(20%) × 价格分(20%)
```

### AI调价建议

```
1. 价格弹性分析（变异系数CV）
2. 竞争定位指数（CPI）
3. 需求强度判断（HIGH/MEDIUM/LOW）
4. 三档策略输出（保守/标准/激进）
```

---

## 项目结构

```
hotel-compete-report/
├── core/                          # 核心引擎
│   ├── competitor_filter.py       # 多维竞品评分
│   └── amap_client.py            # amap-sdk封装
├── industry_search/               # 行业扩展
│   └── multi_industry.py         # 出行全链检索
├── algorithm/                     # 调价算法
│   └── pricing_advisor.py        # AI调价建议
└── scripts/
    └── build_compete_report.py   # 竞品报告生成
```

---

## 验证数据（天津瑞湾开元名都，五一假期）

| 竞品 | 平日价 | 五一价 | 涨幅 | 评分 |
|------|--------|--------|------|------|
| 天津于家堡洲际 | ¥916 | ¥1397 | +52.5% | 54分 |
| 天津滨海皇冠假日 | ¥848 | ¥1349 | +59.1% | 排除（距离5.1km）|
| 天津万丽泰达 | ¥721 | ¥1108 | +53.7% | 排除（距离6.3km）|
| 天津泰达万豪 | ¥673 | ¥1026 | +52.5% | 60分 |

**推荐定价（三档）：**
- 保守：¥640（+44.6%）
- 标准：¥697（+57.5%）
- 激进：¥722（+63.0%）⭐

---

## 开源协议

MIT License

## GitHub

https://github.com/chaoliuzhu65-tech/hotel-compete-report
