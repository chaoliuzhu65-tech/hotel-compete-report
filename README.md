# hotel-compete-report v3.0

> 德胧酒店集团 AI-native 市场收益管理工具
> 酒店竞品价格监测 + 行业扩展检索 + AI调价建议引擎

[🏠 中文Skill说明](SKILL.md) | [📖 改进日志v3.1](#v31-改进亮点)

---

## 核心能力

| 能力 | 技术 | 状态 |
|------|------|------|
| 高德POI精准定位 | amap-sdk官方SDK | ✅ |
| 飞猪实时价格采集 | Fliggy API | ✅ |
| 多维竞品评分 v2 | **动态权重+异常过滤+TopN精选+occupancy加分** | ✅ v3.1新增 |
| 行业扩展检索 | 酒店/餐饮/零售/银行/出行全链 | ✅ |
| **🧳 出行AI伴侣** | 关键字查询周边美食/交通/景区，变身个人出行助手 | ✅ v3.2新增 |
| AI调价建议 | 价格弹性+CPI+需求信号算法 | ✅ |
| 每日定时监测 | Cron定时任务+飞书推送 | ✅ |
| 导出报告 | Markdown / HTML / PDF | ✅ |

---

## 快速开始

```bash
# 1. 安装
pip install -r requirements.txt
export AMAP_MAPS_API_KEY="你的Key"

# 2. 竞品价格分析
python3 algorithm/pricing_advisor.py
# → 推荐价格：¥722（激进）/ ¥697（标准）/ ¥640（保守）

# 3. 批量生成多家酒店报告
python3 scripts/generate_batch_reports.py --input examples/three_hotels.json --output reports --api-key YOUR_KEY
# → 生成Markdown + HTML 双格式

# 4. 🧳 出行AI伴侣 - 关键字查询周边
python3 scripts/travel_assistant.py --hotel "天津瑞湾开元名都" --lat 39.021567 --lon 117.745689 --query "周边有什么好吃的"
# → 自动识别关键字，返回美食推荐

# 5. 出行全链行业扩展
python3 industry_search/multi_industry.py
# → 住宿38家 | 餐饮49家 | 出行23家 | 购物45家 | 金融37家
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
│   ├── competitor_filter.py       # 多维竞品评分 v1
│   ├── competitor_filter_v2.py   # 🆕 多维竞品评分 v2（优化版）
│   └── amap_client.py            # amap-sdk封装
├── industry_search/               # 行业扩展
│   └── multi_industry.py         # 出行全链检索
├── algorithm/                     # 调价算法
│   └── pricing_advisor.py        # AI调价建议
├── scripts/
│   ├── build_compete_report.py   # 竞品报告生成
│   ├── generate_batch_reports.py # 🆕 批量生成报告（Markdown/HTML）
│   ├── travel_assistant.py       # 🆕 出行AI伴侣 - 关键字查询周边
│   └── export_pdf.py             # 🆕 HTML导出PDF
├── examples/                      # 示例
│   └── three_hotels.json         # 三家开元酒店示例
├── reports/                       # 生成的报告
├── docs/                           # 文档
│   ├── 技术说明-调价策略.md
│   └── 德胧集团内部部署说明.md
└── requirements.txt               # 依赖清单
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

## v3.1 改进亮点（基于开源社区同类项目借鉴）

### 竞品选择逻辑优化

**原来的问题：** 固定权重一刀切，没有异常过滤，不考虑occupancy信号

**新增改进：**

1. **分层筛选流程**
   - 第一层：距离硬过滤（超过阈值直接排除）
   - 第二层：星级匹配过滤
   - 第三层：**IQR异常值自动过滤** → 排除满房天价/促销超低价干扰
   - 第四层：多维加权评分 → **支持动态权重**
   - 第五层：**TopN精选输出** → 只保留最相关的3-8家竞品，避免信号稀释

2. **动态权重场景预设**
   ```python
   from core.competitor_filter_v2 import get_config_for_scenario
   config = get_config_for_scenario("downtown")  # 市中心：距离权重40%
   config = get_config_for_scenario("resort")     # 度假景区：星级权重40%
   config = get_config_for_scenario("price_battle") # 价格战：价格权重40%
   ```

3. **Occupancy信号利用**
   - 竞品满房 +10分 → 更大提价空间
   - 竞品高入住 +5分

4. **完全向后兼容**，v1 API保持不变

---

## v3.2 新增：出行AI伴侣 🧳

**激活方式**：关键字自然语言查询 → 自动识别意图，返回对应周边设施

支持查询：
- 周边美食/餐厅 → 返回美食推荐列表，按距离排序
- 地铁站/公交站 → 最近的交通设施
- 银行/ATM → 金融配套
- 景区/公园 → 周边旅游景点
- "全部"/"综合" → 返回全行业配套报告

**使用示例**：
```bash
python scripts/travel_assistant.py \
  --hotel "天津瑞湾开元名都" \
  --lat 39.021567 \
  --lon 117.745689 \
  --query "周边有什么好吃的"
```

输出：Markdown + HTML 双格式，手机打开HTML就能看。

## v3.1 改进亮点（基于开源社区同类项目借鉴）

### 竞品选择逻辑优化

**原来的问题：** 固定权重一刀切，没有异常过滤，不考虑occupancy信号

**新增改进：**

1. **分层筛选流程**
   - 第一层：距离硬过滤（超过阈值直接排除）
   - 第二层：星级匹配过滤
   - 第三层：**IQR异常值自动过滤** → 排除满房天价/促销超低价干扰
   - 第四层：多维加权评分 → **支持动态权重**
   - 第五层：**TopN精选输出** → 只保留最相关的3-8家竞品，避免信号稀释

2. **动态权重场景预设**
   ```python
   from core.competitor_filter_v2 import get_config_for_scenario
   config = get_config_for_scenario("downtown")  # 市中心：距离权重40%
   config = get_config_for_scenario("resort")     # 度假景区：星级权重40%
   config = get_config_for_scenario("price_battle") # 价格战：价格权重40%
   ```

3. **Occupancy信号利用**
   - 竞品满房 +10分 → 更大提价空间
   - 竞品高入住 +5分

4. **完全向后兼容**，v1 API保持不变

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
python scripts/publish_to_feishu.py --input test_output/README.md --folder-token "你的文件夹token"
```

**特点：**
- ✅ 直接创建为飞书云文档，**无GitHub Pages缓存延迟**，打开就是最新
- ✅ 同名文档会自动创建新版本，不会覆盖历史
- ✅ 权限继承自飞书云文件夹，方便德胧内部同事协作查看

---

## 同类开源项目参考

- [autumn-agentic-copilot](https://github.com/Moriyan1307/autumn-agentic-copilot) - 多智能体AI收益管理系统，借鉴了自然语言策略配置思想
- [hotel-revenue-management](https://github.com/Naresh1401/hotel-revenue-management) - 机器学习动态定价，借鉴了RevPAR优化思路
- [talya-project](https://github.com/YusufTasoglu/talya-project) - 网页爬虫方案，可作为API采集的补充

---

## GitHub

https://github.com/chaoliuzhu65-tech/hotel-compete-report
