# 🏨 hotel-compete-report v2.0

> 酒店竞品价格分析报告生成器 | Hotel Competitor Price Analysis Report Generator

德胧 AI 实验室开源作品 | 开源协议：MIT

**高德地图 POI 精准定位 + 飞猪 Fliggy 实时价格 = 全网最准竞品分析**

---

## ✨ 功能特性

- 🗺️ **高德地图 POI 精准定位**：已知竞品名称 → 100%找到坐标（解决飞猪搜索覆盖度不足问题）
- 📊 **飞猪实时价格**：假期价 + 平日价双查询，计算真实涨幅
- 🔢 **双重校准定价算法**：涨幅校准 + 绝对值校准，输出三档策略
- 📄 **结构化报告**：Markdown + HTML + JSON，同时输出
- 🤖 **多 AI 工具兼容**：OpenClaw / Trae / CodeBuddy / Coze / 妙搭

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- （可选）高德地图 API Key（用于 POI 精准定位）
- （可选）flyai CLI（用于飞猪价格数据）

### 安装

```bash
git clone https://github.com/delonix-ai/hotel-compete-report.git
cd hotel-compete-report
pip install requests
```

### 配置高德 API Key（推荐）

```bash
# 方式1：环境变量
export AMAP_MAPS_API_KEY="你的后端API Key"

# 方式2：配置文件
echo "你的后端API Key" > ~/.config/amap-apikey
```

### 使用方法

```bash
AMAP_MAPS_API_KEY="0f9da10a87fa96c564f2d3d0f459fd6f" \
python scripts/build_compete_report.py \
  --hotel "天津瑞湾开元名都" \
  --target-date 2026-05-01 \
  --competitors 8 \
  --scope 滨海 \
  --base-price 443
```

### 输出示例

```
推荐价格：保守 ¥642 | 标准 ¥677 ⭐ | 激进 ¥713

输出文件：
  output/hotel-compete-report/
  ├── 天津瑞湾开元名都_20260501_竞品价格分析报告.md
  ├── 天津瑞湾开元名都_20260501_pricing_recommendation.json
  └── 天津瑞湾开元名都_20260501_raw_data.json
```

---

## 📐 双重校准定价算法

```
第一步：涨幅校准
  → 计算竞品涨幅中位数（抗异常值）
  → 我店涨幅 = 竞品涨幅中位数 ±15%

第二步：绝对值校准
  → 推荐价格 ≤ 竞品最高 × 0.95
  → 推荐价格 ≥ 竞品最低 × 1.1

第三步：三档策略
  → 保守 = min(绝对值上限, 涨幅下限)
  → 标准 = (涨幅下限 + min(绝对值上限, 涨幅上限)) / 2  ← 推荐
  → 激进 = min(绝对值上限, 涨幅上限)
```

---

## 🤝 接入其他 AI 工具

### OpenClaw
将 hotel-compete-report 目录放入 ~/.openclaw/workspace/skills/ 即可自动识别。

### Trae / CodeBuddy
```bash
AMAP_MAPS_API_KEY="你的Key" python scripts/build_compete_report.py --hotel "你的酒店" --target-date 2026-05-01 --base-price 400
```

### Coze / 妙搭
使用 build_compete_report.py 作为工作流节点，输入参数：hotel, target_date, competitors, scope, base_price。

---

## 📁 项目结构

```
hotel-compete-report/
├── SKILL.md                     # Skill 定义文件（OpenClaw 格式）
├── README.md                    # 本文件
├── LICENSE                      # MIT 开源协议
├── _meta.json                   # 包元数据
├── scripts/
│   └── build_compete_report.py  # 核心脚本（高德POI+飞猪双引擎）
└── references/
    ├── SOP.md                  # 调研标准作业流程
    └── output_spec.md           # 报告验收标准
```

---

## 🔧 高德 MCP Server（可选）

```bash
pip install amap-mcp-server
AMAP_MAPS_API_KEY="你的Key" python -m amap_mcp_server stdio
```

---

**德胧 AI 实验室出品** | 2026年4月 | v2.0
