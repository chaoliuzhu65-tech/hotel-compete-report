# 🛠️ 工具、SKILL 与 MCP 完整清单

> 本清单记录生成「德胧竞品价格监控报告」所使用的全部工具、SKILL 和 MCP 配置  
> 供其他AI伙伴或同事参考复制  
> 更新时间：2026-04-14

---

## 一、AI Agent 平台

| 平台 | 版本 | 说明 |
|------|------|------|
| **WorkBuddy + Claw** | Auto | 主力开发平台，具备代码生成、文件操作、命令执行、网络请求等原生能力 |
| 飞书 AI 神灯（小云） | 最新 | 飞书生态内AI助手，负责飞书文档推送、群消息通知 |
| 有道龙虾（Lobster） | 最新 | 知识管理协作，负责行业报告归档 |

---

## 二、MCP 配置清单

以下MCP在 `~/.workbuddy/mcp.json` 中配置：

### 2.1 飞猪AI (`flyai-cli`)
```json
{
  "flyai": {
    "command": "npx",
    "args": ["-y", "@fly-ai/flyai-cli"],
    "description": "飞猪实时酒店/机票价格查询，无需API Key"
  }
}
```
**用途：** 查询竞品酒店在飞猪的实时价格（含节假日价格）

### 2.2 高德地图 (`amap-jsapi`)
```json
{
  "amap": {
    "command": "npx",
    "args": ["-y", "amap-jsapi-mcp"],
    "env": {
      "AMAP_KEY": "0f9da10a87fa96c564f2d3d0f459fd6f"
    }
  }
}
```
**用途：** POI周边搜索（找竞品）、路径规划

### 2.3 12306 MCP
```json
{
  "12306": {
    "command": "npx",
    "args": ["-y", "12306-mcp"],
    "description": "12306火车票实时查询，v0.3.8，MIT License"
  }
}
```
**用途：** 获取铁路余票率（作为出行需求强度信号）

### 2.4 飞书 OpenAPI（可选，用于推送报告）
```json
{
  "feishu": {
    "command": "npx",
    "args": ["-y", "feishu-mcp"],
    "env": {
      "FEISHU_APP_ID": "cli_xxxx",
      "FEISHU_APP_SECRET": "xxxx"
    }
  }
}
```

### 2.5 Tavily Search（新闻情报）
```json
{
  "tavily": {
    "command": "npx",
    "args": ["-y", "@tavily/mcp"],
    "env": {
      "TAVILY_API_KEY": "tvly-xxxx"
    }
  }
}
```
**用途：** 搜索竞品酒店新闻动态、节假日流量预测新闻

---

## 三、SKILL 清单

| SKILL名称 | 位置 | 版本 | 触发词 |
|----------|------|------|--------|
| **competitor-price-monitor** | `~/.workbuddy/skills/competitor-price-monitor/` | v1.0 | "竞品价格监控"、"价格监测" |
| **delonix-travel-planner** | `~/.workbuddy/skills/delonix-travel-planner/` | v3.1 | "商旅规划"、"出差行程" |
| **leisure-travel-planner** | `~/.workbuddy/skills/leisure-travel-planner/` | v1.1 | "旅游攻略"、"出去玩" |
| **universal-travel-planner** | `~/.workbuddy/skills/universal-travel-planner/` | v1.1 | "出行规划"、"订酒店" |
| **feishu-integration** | `~/.workbuddy/skills/feishu-integration/` | 最新 | "发飞书"、"推送文档" |
| **dingtalk-integration** | `~/.workbuddy/skills/dingtalk-integration/` | 最新 | "发钉钉"、"钉钉通知" |

---

## 四、API Keys 配置

> ⚠️ 以下Key仅供德胧集团内部AI伙伴参考，外部人员请自行申请

| 服务 | Key类型 | 申请地址 | 用途 |
|------|--------|---------|------|
| 高德地图（前端JS） | Web JS Key | https://console.amap.com | HTML报告中地图渲染 |
| 高德地图（后端） | Web Service Key | https://console.amap.com | POI搜索、路径规划 |
| 飞猪 flyai-cli | 无需Key | NPM直接安装 | 实时价格采集 |
| Tavily | API Key | https://tavily.com | 新闻搜索 |
| 飞书 OpenAPI | App ID + Secret | https://open.feishu.cn | 文档推送 |

---

## 五、Python 依赖

```txt
# requirements.txt
requests>=2.28.0
python-dateutil>=2.8.2
```

> 系统依赖极少，无需安装大型框架。所有AI能力通过MCP协议调用。

---

## 六、HTML报告生成原理

> **常见误解：** 认为需要专门的"报告SKILL"才能生成漂亮的HTML报告

**真相：WorkBuddy Claw 原生代码能力直接生成，无需任何专属SKILL。**

生成流程：
```
1. Python 脚本（scripts/gen_report.py）
   ↓ 接收：竞品数据 + 价格数据 + 算法结果
2. 使用 Python f-string 拼接 HTML
   ↓ 模板内嵌 CSS（德胧深蓝+金色色系）+ JavaScript（图表交互）
3. WorkBuddy write_to_file 工具
   ↓ 写入 .html 文件
4. WorkBuddy execute_command 工具
   ↓ git add + git commit + git push
5. GitHub Pages
   → 自动部署，全球可访问
```

**核心设计参考：**
- 德胧品牌色：`#1E3A8A`（深蓝）+ `#F59E0B`（金色）
- 字体：系统字体栈，无CDN依赖
- 响应式：CSS Grid + Flexbox，无需Bootstrap/Tailwind
- 图表：纯CSS进度条，无需Chart.js

---

## 七、复制本系统的完整步骤

其他AI伙伴或同事如需为自己酒店部署相同能力：

```bash
# Step 1: 克隆仓库
git clone https://github.com/chaoliuzhu65-tech/hotel-compete-report.git

# Step 2: 安装Python依赖
pip install -r requirements.txt

# Step 3: 配置环境变量
export AMAP_MAPS_API_KEY="你的高德Web服务Key"

# Step 4: 添加酒店信息（编辑 scripts/generate_batch_reports.py）
HOTELS = [
    {
        "name": "你的酒店名称",
        "coords": "经度,纬度",
        "base_price": 平日均价,
        "competitor_radius": 5000  # 搜索半径，单位米
    }
]

# Step 5: 运行生成报告
python3 scripts/generate_batch_reports.py

# Step 6: 推送到GitHub Pages（如果有自己的仓库）
git add . && git commit -m "新增酒店报告" && git push
```

---

*清单生成：2026-04-14 by Claw × WorkBuddy*
