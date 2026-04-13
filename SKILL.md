# hotel-compete-report Skill v3.3

> 德胧酒店集团 AI-native 市场收益管理工具
> 酒店竞品价格监测 + 行业扩展检索 + AI调价建议 + 飞书云文档直接发布 + 🧳出行AI伴侣

---

## 📁 输出目录结构（天然满足多场景管理）

```
output/                           # 输出根目录
├── {hotel-slug}/                 # 按酒店分目录，一家酒店一个目录
│   ├── {hotel-slug}-YYYY-MM-DD.md    # 按日期存档，保留历史版本
│   ├── {hotel-slug}-YYYY-MM-DD.html
│   └── {hotel-slug}-latest.*          # 软链接指向最新版本
├── travel-assistant/            # 🧳 出行AI伴侣临时查询输出
│   └── {hotel-slug}-{query-slug}.html  # 每个查询一个HTML，手机直接打开
└── README.md                    # 总索引，列出所有酒店最新报告链接
```

**满足你的需求：**
- ✅ 一家酒店每日监测更新 → 按日期存档，保留历史，方便对比价格变化
- ✅ 个人出行AI伴侣临时查询 → 独立目录，不会干扰价格监测，手机HTML直接打开
- ✅ 多家酒店不混乱 → 按酒店分目录，总索引方便导航
- ✅ 平衡取舍 → 结构清晰但不复杂，够用就好

---

## 🚀 五种使用方式（自然语言也能用）

### 方式一：自然语言对话使用（推荐给德胧同事）

你只需要说清楚：
```
帮我生成"杭州千岛湖开元度假村"五一竞品调价报告
平日价格是580，位置坐标...
```

我会帮你：
1. 自动调用 `generate_single_report.py`
2. 按日期保存到对应目录
3. 更新总索引
4. 如果你需要，可以直接发布到飞书云文档

### 方式二：单家酒店日常监测（每日更新）

```bash
python scripts/generate_single_report.py \
  --name "天津瑞湾开元名都大酒店" \
  --brand "开元名都" \
  --star "五星级/豪华型" \
  --weekday-price 443 \
  --target-date 2026-05-01 \
  --lat 39.000893 \
  --lon 117.710212 \
  --district "天津市滨海新区" \
  --output output \
  --api-key YOUR_AMAP_KEY
```

### 方式三：多家酒店批量生成

```bash
# 编辑 examples/three_hotels.json 添加多家酒店信息
python3 scripts/generate_batch_reports.py --input examples/three_hotels.json --output reports --api-key $AMAP_MAPS_API_KEY
```

### 方式四：🧳 出行AI伴侣 - 自然语言查询周边

```bash
# 直接用自然语言问
python3 scripts/travel_assistant.py \
  --hotel "天津瑞湾开元名都" \
  --lat 39.021567 \
  --lon 117.745689 \
  --query "周边有什么好吃的火锅推荐"
# → 自动生成手机友好HTML，直接分享到微信/飞书
```

支持关键词：
- 美食相关：`好吃` `美食` `吃饭` `火锅` `烧烤`
- 交通出行：`地铁` `公交` `火车站` `机场`
- 购物：`购物` `商场` `超市`
- 金融：`银行` `ATM`
- 景点：`景点` `景区` `公园`
- 全部：`全部配套` `综合配套`

### 方式五：发布到飞书云文档（德胧内部）

```bash
export FEISHU_APP_ID="你的AppID"
export FEISHU_APP_SECRET="你的AppSecret"

python scripts/publish_to_feishu.py --input output/README.md --folder-token "你的云文件夹token"
```

---

## 🎯 核心设计哲学（v3.2+）

> **AI用精选保证准确，决策者看分组看到完整格局**

| 分组 | 用途 | 参与AI调价？ |
|------|------|--------------|
| **强相关竞品** | AI调价分析使用 | ✅ 是 |
| **外资品牌竞品** | 市场分层观测 | ❌ 否 |
| **内资品牌竞品** | 市场分层观测 | ❌ 否 |
| **低价位区（<0.7×目标）** | 价格分层观测 | ❌ 否 |
| **中价位区（0.7~1.3×目标）** | 价格分层观测 | ❌ 否 |
| **高价位区 (>1.3×目标)** | 价格分层观测 | ❌ 否 |

### 自动半径扩展

- 如果初始半径（默认5km）找不到≥3家强相关竞品，自动扩展：
- 5km → 10km → 15km
- 解决度假酒店周边竞品太少的问题

---

## 📊 多维评分体系

```
竞品得分 = 距离分(30%) × 星级分(30%) × 品牌分(20%) × 价格分(20%) + occupancy加分

距离分：≤1km=100分, ≤3km=80分, ≤5km=60分, >5km=0分
星级分：同档=100, 相邻=60, 相差2档=20, 未知=50
品牌分：同档次=100, 相邻=70, 其他=50
价格分：±30%重叠=100, ±50%=60, >50%=20
```

---

## 💡 调价算法核心逻辑

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

## 📤 发布方式

### 方式一：GitHub Pages 静态网页（公开可访问）

```bash
# 批量生成到docs目录
python scripts/generate_batch_reports.py --input examples/three_hotels.json --output docs --api-key YOUR_KEY
git add docs/ && git commit -m "update reports" && git push
```

**特点：**
- ✅ 每家酒店生成独立HTML文件，文件名唯一（按酒店名slug），**不会相互覆盖**
- ✅ 自动生成README索引页，包含所有报告链接
- ✅ GitHub Pages免费托管，任何人都可以访问

### 方式二：飞书云文档（德胧内部同事使用）

```bash
# 设置飞书凭证（需要开发者后台创建应用）
export FEISHU_APP_ID="你的AppID"
export FEISHU_APP_SECRET="你的AppSecret"

# 批量发布到飞书云空间
python scripts/publish_to_feishu.py --input output/README.md --folder-token "你的文件夹token"
```

**特点：**
- ✅ 直接创建为飞书云文档，**无GitHub Pages缓存延迟**，打开就是最新
- ✅ 同名文档会自动创建新版本，不会覆盖历史
- ✅ 权限继承自飞书云文件夹，方便德胧内部同事协作查看

---

## ⏰ 定时任务（每日自动监测）

```bash
# 每日08:00自动执行
0 8 * * * cd /root/.openclaw/workspace/hotel-compete-report && \
  python3 scripts/generate_single_report.py \
    --name "天津瑞湾开元名都大酒店" \
    --brand "开元名都" \
    --star "五星级/豪华型" \
    --weekday-price 443 \
    --target-date $(date -d+1day +\%Y-\%m-\%d) \
    --lat 39.000893 \
    --lon 117.710212 \
    --district "天津市滨海新区" \
    --output output \
    --api-key $AMAP_MAPS_API_KEY
```

---

## v3.3 更新日志

| 功能 | 说明 |
|------|------|
| ✅ **按酒店分目录按日期存档** | 支持同一酒店每日监测，保留历史方便对比 |
| ✅ **出行AI伴侣独立目录** | 个人查询不干扰价格监测，HTML手机直接打开 |
| ✅ **自然语言使用说明** | 德胧同事不用记命令，直接自然语言说需求就行 |
| ✅ **软性分组筛选** | 强相关用于AI调价，全部分组用于市场观测 |
| ✅ **自动半径扩展** | 5km→10km→15km，解决度假村竞品太少 |
| ✅ **品牌分组展示** | 外资/内资分开统计，方便观察市场格局 |
| ✅ **价格区间分组** | 低/中/高价位各选最多10家展示 |
| ✅ **飞书云直接发布** | 无GitHub Pages缓存延迟 |

---

## GitHub

- 仓库：https://github.com/chaoliuzhu65-tech/hotel-compete-report
- v3.3发布：https://github.com/chaoliuzhu65-tech/hotel-compete-report/releases/tag/v3.3

## 依赖

```
amap-sdk>=0.1.0
pandas
requests
openai（用于AI调价建议）
lark-sdk（飞书云文档发布需要）
```
