---
name: hotel-compete-report
description: 酒店竞品价格分析报告生成器 v2.0。输入酒店名称、目标日期、竞品列表，通过高德地图POI精准定位竞品酒店坐标 + 飞猪Fliggy实时价格API，生成含双重校准定价算法的结构化竞品报告。内置滨海核心竞品库，支持一键部署到任意AI工具。触发词：竞品报告、竞品分析、价格分析、假期定价、调价建议、酒店调研。
version: 2.0.0
author: 德胧AI实验室
tags: [hotel, revenue-management, competitive-analysis, pricing, fliggy, amap, gaode, 高德, 飞猪]
---

# 酒店竞品价格分析报告 Skill v2.0

> **核心升级 v2.0**：高德地图 POI 精准定位（解决飞猪搜索覆盖度不足问题）+ 强制真实数据（禁止演示数据）

## 架构：双引擎数据采集

```
高德地图 POI ──→ 精准定位竞品酒店坐标 + 评分
     ↓
飞猪 Fliggy ──→ 获取实时价格（假期价 + 平日价）
     ↓
双重校准算法 ──→ 输出三档定价策略
```

**为什么需要双引擎？**
- 飞猪搜索覆盖度有限：洲际/皇冠假日等高端品牌可能不出现在搜索结果中
- 高德 POI 可精确定位：已知酒店名称 → 100%找到 → 合并飞猪价格数据

## 环境配置

### 1. 高德地图 API Key（推荐，用于 POI 精准定位）

**申请地址**：https://console.amap.com/dev/key/app

**配置方式（任选一种）**：

```bash
# 方式1：环境变量（推荐）
export AMAP_MAPS_API_KEY="你的后端API Key"

# 方式2：命令行参数
python build_compete_report.py --amap-key "你的后端API Key" ...

# 方式3：配置文件
echo "你的后端API Key" > ~/.config/amap-apikey
```

### 2. 飞猪数据源

```bash
# 安装 flyai CLI 并登录
npm install -g flyai
flyai login
```

## 使用示例

```bash
# 标准调用（高德POI + 飞猪价格）
AMAP_MAPS_API_KEY="0f9da10a87fa96c564f2d3d0f459fd6f" \
python build_compete_report.py \
  --hotel "天津瑞湾开元名都" \
  --target-date 2026-05-01 \
  --competitors 8 \
  --scope 滨海 \
  --base-price 443 \
  --output-dir output/hotel-compete-report

# 只用飞猪（无高德 Key）
python build_compete_report.py \
  --hotel "天津瑞湾开元名都" \
  --target-date 2026-05-01 \
  --competitors 8 \
  --base-price 443
```

## 输入参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--hotel` | ✅ | 目标酒店名称 |
| `--target-date` | ✅ | 目标日期 YYYY-MM-DD |
| `--base-price` | ✅ | 我店平日价（人民币） |
| `--competitors` | ○ | 竞品数量（默认8） |
| `--scope` | ○ | 调研范围：滨海/市区/全域（默认滨海） |
| `--amap-key` | ○ | 高德 API Key（环境变量 AMAP_MAPS_API_KEY 也可） |

## 输出文件

```
output/hotel-compete-report/
  ├── {酒店名}_{日期}_竞品价格分析报告.md    # 主报告
  ├── {酒店名}_{日期}_竞品价格分析报告.html  # HTML版
  ├── pricing_recommendation.json             # 调价建议JSON（供PMS对接）
  └── raw_data.json                          # 原始数据存档
```

## 报告结构

1. **核心发现**：竞品价格对比表 + 关键洞察
2. **定价建议**：三档策略（保守/标准/激进）+ 房型分级
3. **行动建议**：立即行动 + 持续监测
4. **数据附录**：竞品详细信息 + 算法参数
5. **方法论沉淀**：SOP + 注意事项

## 双重校准算法

```
第一重：涨幅校准
  → 计算竞品涨幅中位数（抗异常值）
  → 我店涨幅 = 竞品涨幅中位数 ±15%

第二重：绝对值校准
  → 推荐价格 ≤ 竞品最高 × 0.95（溢价空间保护）
  → 推荐价格 ≥ 竞品最低 × 1.1（防止价格战）

三档策略：
  保守 = min(绝对值上限, 涨幅下限)
  标准 = (涨幅下限 + min(绝对值上限, 涨幅上限)) / 2  ← 推荐
  激进 = min(绝对值上限, 涨幅上限)
```

## 内置竞品库（滨海核心区）

```python
BINHAI_COMPETITORS = [
    "天津于家堡洲际酒店",
    "天津滨海皇冠假日酒店",
    "天津万丽泰达酒店",
    "天津滨海泰达万豪行政公寓",
    "滨海一号酒店",
    "天津滨海圣光皇冠假日酒店",
]
```

## 接入其他 AI 工具

### OpenClaw

将 `hotel-compete-report` 目录放入 `~/.openclaw/workspace/skills/`

### Trae / CodeBuddy

```bash
git clone https://github.com/delonix-ai/hotel-compete-report.git
cd hotel-compete-report
AMAP_MAPS_API_KEY="你的Key" python scripts/build_compete_report.py ...
```

### Coze / 妙搭

在 Workflow 中调用 `build_compete_report.py`，参数：
- `hotel`: 目标酒店名称
- `target_date`: YYYY-MM-DD
- `competitors`: 数量
- `base_price`: 平日价

### MCP 集成（高德 MCP Server）

如需在其他 MCP 客户端使用高德地图：

```bash
# 安装高德 MCP Server
pip install amap-mcp-server

# 启动 MCP Server
AMAP_MAPS_API_KEY="你的Key" python -m amap_mcp_server stdio
```

## 数据质量规则

- ⚠️ **禁止使用演示/虚拟数据** — 所有数据必须来自真实API
- 飞猪价格可能波动，建议多平台交叉验证
- 高德 POI 优先于飞猪搜索定位（更精准）
- 平日价取假期前14天同星期日期价格对比
