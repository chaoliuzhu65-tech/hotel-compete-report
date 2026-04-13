# hotel-compete-report Skill v3.2

> 德胧酒店集团 AI-native 市场收益管理工具
> 酒店竞品价格监测 + 行业扩展检索 + AI调价建议 + 飞书云文档直接发布

---

## 五大核心模块

| 模块 | 路径 | 功能 |
|------|------|------|
| **多维软性分组筛选 v2.1** | `core/competitor_filter_v2.py` | 强相关用于AI，全部分组用于市场观测 |
| **amap-sdk封装** | `core/amap_client.py` | 官方Python SDK（替代CLI）|
| **行业扩展检索** | `industry_search/multi_industry.py` | 酒店/餐饮/零售/银行/出行全链 |
| **AI调价建议引擎** | `algorithm/pricing_advisor.py` | 弹性分析+CPI定位+三档策略 |
| **🧳 出行AI伴侣** | `scripts/travel_assistant.py` | 自然语言查询周边，变身出行助手 |

---

## 快速使用

### 1. 安装依赖

```bash
pip install amap-sdk pandas openai lark-sdk
export AMAP_MAPS_API_KEY="你的高德Key"
```

### 2. 批量生成多家酒店报告

```bash
# 输入JSON，输出Markdown + HTML双格式
python3 scripts/generate_batch_reports.py --input examples/three_hotels.json --output reports --api-key $AMAP_MAPS_API_KEY
```

### 3. 🧳 出行AI伴侣 - 自然语言查询周边

```bash
python3 scripts/travel_assistant.py --hotel "天津瑞湾开元名都" --lat 39.021567 --lon 117.745689 --query "周边有什么好吃的推荐"
# → 自动识别分类，返回HTML报告
```

---

## 软性分组筛选 v3.2 核心设计

### 设计哲学

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

## 多维评分体系

```
竞品得分 = 距离分(30%) × 星级分(30%) × 品牌分(20%) × 价格分(20%) + occupancy加分

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

## 📤 发布方式

### 方式一：GitHub Pages 静态网页（公开可访问）

```bash
# 批量生成到docs目录
python scripts/generate_batch_reports.py --input examples/three_hotels.json --output docs --api-key YOUR_KEY

# 提交到GitHub，自动通过GitHub Pages发布
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

## v3.2 更新日志

| 功能 | 说明 |
|------|------|
| **软性分组筛选** | 强相关用于AI调价，全部分组用于市场观测，不丢失潜在信息 |
| **自动半径扩展** | 5km→10km→15km，解决度假村竞品太少问题 |
| **品牌分组展示** | 外资/内资分开统计，方便观察市场格局 |
| **价格区间分组** | 低/中/高价位各选最多10家展示，完整市场分层 |
| **飞书云发布** | 直接推送到飞书云文档，无缓存延迟 |
| **🧳 出行AI伴侣** | 自然语言查询周边美食/交通/景点 |

---

## GitHub

- 仓库：https://github.com/chaoliuzhu65-tech/hotel-compete-report
- v3.2发布：https://github.com/chaoliuzhu65-tech/hotel-compete-report/releases/tag/v3.2

## 依赖

```
amap-sdk>=0.1.0
pandas
requests
openai（用于AI调价建议）
lark-sdk（飞书云文档发布需要）
```
