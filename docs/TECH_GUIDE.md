# 🏨 德胧酒店竞品价格监控系统 · 技术说明文档

> **版本：** v4.2 · 2026-04-14  
> **项目：** hotel-compete-report  
> **维护方：** Claw（WorkBuddy AI）× 小云（飞书AI神灯）× 晁留柱小八  
> **仓库：** https://github.com/chaoliuzhu65-tech/hotel-compete-report  
> **线上地址：** https://chaoliuzhu65-tech.github.io/hotel-compete-report/

---

## 一、系统定位与设计理念

本系统专为**德胧酒店集团旗下各中高端物业**设计，解决以下核心痛点：

| 痛点 | 传统方式 | 本系统方案 |
|------|---------|-----------|
| 竞品选择不准 | 人工查找，依赖主观经验 | 高德POI API精准圆形搜索，5km内同档位酒店 |
| 价格数据滞后 | 手动登录OTA查价 | 飞猪AI MCP实时采集，无需API Key |
| 调价凭感觉 | 主观判断 | 三层弹性算法（CPI×需求×竞品）三档策略 |
| 数据假繁荣 | 只看交通数据 | 四层舆情判断，识别穷游/特种兵"假繁荣" |
| 报告不美观 | 纯文字 | 响应式HTML，德胧品牌色系，移动端友好 |

---

## 二、技术架构

```
┌──────────────────────────────────────────────────────────────────┐
│                  德胧竞品智能监控系统 v4.2                         │
│                                                                  │
│  输入层：酒店名称 + 坐标（经纬度）+ 监测日期                        │
│                         ↓                                        │
│  数据采集层                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐     │
│  │  高德地图API  │  │  飞猪AI MCP  │  │  Tavily 新闻搜索   │     │
│  │  POI周边发现  │  │  实时价格采集 │  │  行业舆情/会展情报  │     │
│  │  5km内同档酒店│  │  五一/节假日  │  │  竞品动态          │     │
│  └──────┬───────┘  └──────┬───────┘  └────────┬───────────┘     │
│         └─────────────────┴──────────────────┘                  │
│                            ↓                                     │
│  算法引擎层（revenue_advisor.py）                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Layer1：社交舆情分析（小红书穷游比例 → 假繁荣检测）          │   │
│  │  Layer2：交通数据（12306余票率 → 实际出行量估算）             │   │
│  │  Layer3：OTA消费结构（高星占比变化 → 中高端需求强度）          │   │
│  │  Layer4：人工交互补充（客群敏感度、常客比例）                  │   │
│  │                          ↓                                │   │
│  │  三档策略输出：保守（保流量）/ 均衡 / 激进（保溢价）           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                            ↓                                     │
│  输出层                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐     │
│  │  HTML报告    │  │  Markdown报告 │  │  飞书推送           │     │
│  │  德胧品牌设计 │  │  文档归档     │  │  AI研究群/工作群    │     │
│  │  移动端适配   │  │              │  │                    │     │
│  └──────────────┘  └──────────────┘  └────────────────────┘     │
└──────────────────────────────────────────────────────────────────┘
```

---

## 三、核心模块说明

### 3.1 高德POI周边发现（`algorithm/revenue_advisor.py`中的数据采集前置）

**API：** `GET https://restapi.amap.com/v3/place/around`

| 参数 | 值 | 说明 |
|------|----|------|
| `location` | `经度,纬度` | 酒店精确坐标 |
| `radius` | `5000` | 搜索半径5公里 |
| `types` | `110202` | 住宿类-星级酒店 |
| `key` | 后端Web服务Key | `0f9da10a87fa96c564f2d3d0f459fd6f` |

**竞品过滤规则（重要！）：**
- ✅ 保留：同档位内资品牌（开元、亚朵、桔子、铂涛等）
- ✅ 保留：不带国际品牌标识的独立酒店
- ⚠️ 外资联号（万豪、希尔顿、洲际、凯悦）**仅作市场参考，不纳入直接定价对标**
- ❌ 排除：民宿、公寓、青旅（住宿档位差距过大）

### 3.2 飞猪实时价格采集

**工具：** `npx -y @fly-ai/flyai-cli search-hotel`（无需单独API Key）

```bash
# 查询某酒店五一价格
npx -y @fly-ai/flyai-cli search-hotel --hotel "天津于家堡洲际" --checkin 2026-05-01 --checkout 2026-05-02
```

**注意：** flyai-cli 是 WorkBuddy 内置能力的一部分，直接通过 MCP 协议调用，其他AI伙伴部署时需确认 flyai-cli 已安装。

### 3.3 算法引擎（`algorithm/revenue_advisor.py`）

核心类结构：

```python
# 市场舆情数据（四层感知）
MarketSentimentData:
  - xiaohongshu_budget_ratio    # 小红书穷游比例
  - train_sold_out_rate         # 12306余票售罄率
  - ota_luxury_ratio            # 高星OTA占比
  - hotel_corporate_ratio       # 商旅客比例（人工录入）

# 竞品价格数据
CompetitorPrice:
  - name, star                  # 酒店名和星级
  - normal_price, holiday_price # 平日/节假日价格
  - occupancy_hint              # 满房率暗示（OTA可见性估算）

# 收益建议输出
RevenueAdvisor.recommend() -> PricingRecommendation:
  - conservative  # 保守档（保流量，通常为竞品中位价-10%）
  - balanced      # 均衡档（房价+流量双优）
  - aggressive    # 激进档（溢价最大化）
```

**假繁荣识别逻辑：**
```python
if xiaohongshu_budget_ratio > 0.60 and train_sold_out_rate > 0.50:
    → SentimentLevel.FAKE_BOOM  # 需求降级，保守建议
```

### 3.4 HTML报告生成

> **问题：这个漂亮的HTML报告是怎么生成的？用了哪些工具？**

**完整工具链清单：**

| 工具/能力 | 类型 | 用途 |
|---------|------|------|
| WorkBuddy Claw 代码能力 | **原生内置** | 直接在Python中拼接生成HTML字符串，无需任何专属报告SKILL |
| `write_to_file` 工具 | **WorkBuddy原生** | 将生成的HTML内容写入本地文件 |
| `preview_url` 工具 | **WorkBuddy原生** | 在IDE内置浏览器中预览本地HTML |
| `execute_command` 工具 | **WorkBuddy原生** | 运行Python脚本、git push |
| `scripts/gen_report.py` | 本项目Python脚本 | HTML模板填充（竞品表格、价格卡片、品牌色系） |
| 高德POI API | MCP/HTTP | 获取竞品位置数据 |
| 飞猪 flyai-cli | MCP | 获取实时价格数据 |
| Tavily Search | MCP | 获取新闻/行业舆情 |

**结论：HTML报告完全由WorkBuddy原生代码能力生成，无需安装任何专属"报告生成SKILL"。** 德胧品牌色系（深蓝`#1E3A8A` + 金色`#F59E0B`）直接硬编码在HTML模板中。

---

## 四、本次四店五一报告数据来源

| 酒店 | 坐标 | 竞品发现方式 | 价格来源 | 市场情绪 |
|------|------|------------|---------|---------|
| 天津瑞湾开元名都 | 117.710, 39.001 | 高德POI 5km圆形搜索（泰达开发区） | 飞猪实时 | 📊 混合型 |
| 杭州浙旅开元名庭 | 120.219, 30.286 | 高德POI 5km圆形搜索（东站商圈） | 飞猪实时 | ⚠️ 假繁荣 |
| 杭州三立开元名都 | 120.159, 30.311 | 高德POI 5km圆形搜索（城北运河） | 飞猪实时 | 📊 混合型 |
| 北京歌华开元名都 | 116.394, 39.965 | 高德POI 5km圆形搜索（鼓楼后海） | 飞猪实时 | 🔥 真实繁荣 |

---

## 五、关键业务规则（不可变更）

1. **内资品牌不对标外资联号** — 开元系不与万豪/希尔顿直接比价，避免定价偏差
2. **关注涨价后的绝对值** — 不是涨幅百分比，而是最终房价是否仍有竞争力
3. **竞品满房率=需求信号** — 周边酒店满房→可适度上调；周边空房→谨慎上调
4. **假繁荣保护机制** — 小红书穷游流量爆发时，自动降档保守策略，防止错判需求
5. **三策略必须同时输出** — 酒店GM根据自身经营判断选择，系统不代替人做决策

---

## 六、工具/SKILL/MCP 完整清单

| 名称 | 类型 | 版本 | 安装方式 | 必需/可选 |
|------|------|------|---------|---------|
| WorkBuddy Claw | **AI Agent平台** | Auto | 内置 | 必需 |
| 高德地图 Web服务API | HTTP API | v3 | 申请Key: console.amap.com | 必需 |
| 飞猪 flyai-cli | MCP/CLI | 最新 | `npx -y @fly-ai/flyai-cli` | 必需 |
| Tavily Search | MCP | 最新 | WorkBuddy MCP配置 | 推荐 |
| 12306 MCP | MCP | v0.3.8 | `npx -y 12306-mcp` | 推荐 |
| 飞书 OpenAPI | HTTP API | v3 | 飞书开放平台申请 | 可选（推送用） |
| revenue_advisor.py | Python模块 | v2.0 | 本仓库 `algorithm/` | 必需 |
| gen_report.py | Python脚本 | v1.0 | 本仓库 `scripts/` | 推荐 |
| Python 3.10+ | 运行时 | 3.10+ | miniconda / pyenv | 必需 |

---

## 七、部署说明

### GitHub Pages（当前方案）
```bash
git clone https://github.com/chaoliuzhu65-tech/hotel-compete-report.git
# 报告推送后自动部署到 https://chaoliuzhu65-tech.github.io/hotel-compete-report/
```

### 本地运行
```bash
pip install requests
export AMAP_MAPS_API_KEY="0f9da10a87fa96c564f2d3d0f459fd6f"
python3 scripts/generate_batch_reports.py
```

---

## 八、开发路线图

- [x] v1.0 基础价格采集 + 简单对比
- [x] v2.0 假繁荣检测算法 + 四层市场感知
- [x] v3.0 高德POI精准竞品发现 + 多维评分
- [x] v4.0 稳定性测试通过 + 四店五一报告
- [x] v4.2 报告移动端优化 + GitHub Pages部署
- [ ] v5.0 自动定时监测（Cron）+ 飞书定期推送
- [ ] v5.1 阿里云轻量服务器部署 + 移动端Web访问
- [ ] v6.0 磐河数据源接入 + Booking.com价格对比

---

*文档生成时间：2026-04-14 by Claw × WorkBuddy*
