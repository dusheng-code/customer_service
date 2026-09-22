# AI 电商智能客服系统

> 基于 **FastAPI + LangChain + Vue3** 的全栈 AI 客服项目，实现「任务办理 / 知识咨询 / 闲聊」三轨道意图识别与多轮对话管理。

## ✨ 项目简介

这是一个面向电商场景的智能客服系统。用户可以用自然语言办理业务（如退款、查物流）、咨询商品信息，也可以发送**订单卡片 / 商品卡片**（对象消息）与 AI 助手互动。系统核心是一套**多轮对话状态机**：每一轮消息都会经过「意图识别 → 计划校验 → 轨道分发 → 流程推进 → 状态持久化」的完整链路。

## 🎯 核心特性

- **三轨道意图识别**：LLM 作为 Turn Planner，将用户消息规划为三条轨道之一
  - `task` 轨道：办理业务（退款申请、物流查询等），由 YAML 声明式的对话流程引擎驱动
  - `knowledge` 轨道：信息咨询（商品参数、退货政策等），按意图路由到对应知识源检索 + LLM 生成回答
  - `chitchat` 轨道：闲聊兜底，礼貌接话不打断主流程
- **声明式流程引擎**：业务流程（含 `start / collect / action / end` 步骤类型、条件跳转、槽位收集）全部用 YAML 配置，改流程不改代码
- **对象消息（卡片）机制**：前端可一键发送订单/商品卡片，后端自动完成「聚焦对象更新 → 槽位填充 → 流程推进」
- **聚焦对象上下文**：`focused_object` 跨轮次记忆用户当前关注的订单/商品，知识轨道据此校验对象类型并检索真实数据
- **对话状态持久化**：基于 SQLAlchemy 2.0 异步 ORM，每个用户一行 JSON 状态存 MySQL，重启服务会话不丢失
- **计划校验器（Validator）**：LLM 输出的计划先过一道静态校验（意图是否存在、槽位是否齐备、对象类型是否匹配），不合法则转澄清追问，防止幻觉指令直接执行
- **TTS 语音播报 & 一键复制**：机器人回复支持语音朗读与文本复制
- **一键启停脚本**：PowerShell 脚本同时拉起 3 个服务，关掉窗口即全部停止

## 🧱 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 (Composition API) · Vite · 原生 CSS 变量主题 |
| 后端框架 | FastAPI · Uvicorn |
| LLM 编排 | LangChain 1.x (LCEL) · Jinja2 Prompt 模板 · JSON Output Parser |
| 数据库 | MySQL 8 · SQLAlchemy 2.0 (async) · aiomysql |
| HTTP 客户端 | httpx AsyncClient（连接池复用） |
| 依赖管理 | uv + pyproject.toml |
| 服务模拟 | 独立 FastAPI 模拟电商后端（订单/商品/物流 API） |

## 🗂️ 项目结构

```
customer_service/
├── app/                        # 客服后端（核心）
│   ├── api/                    # FastAPI 应用、路由、Pydantic Schema
│   ├── engine/                 # 对话引擎：消息分发、轮次管理、依赖组装
│   ├── plan/                   # Turn Planner（LLM 意图识别）与 Validator
│   ├── task/                   # 任务轨道：流程引擎、Command、Action 注册执行
│   ├── knowledge/              # 知识轨道：意图注册表、Provider、回答生成
│   ├── clarify/                # 澄清追问
│   ├── chitchat/               # 闲聊
│   ├── prompts/jinja2/         # Prompt 模板
│   ├── domain/                 # 领域模型：消息、状态、上下文
│   ├── service/                # 应用服务层（状态读写编排）
│   ├── repository/             # 持久层
│   ├── infrastructure/         # 数据库、LLM、HTTP 客户端等基础设施
│   └── config/                 # pydantic-settings 配置
├── flow_config/                # 声明式对话流程配置（YAML）
│   ├── system_flows.yml        # 系统流程（槽位收集等）
│   └── user_flows.yml          # 业务流程（退款、物流、人工客服等）
├── ecommerce-service-backend/  # 模拟电商后端（提供订单/商品/物流 API）
├── customer-service-frontend/  # Vue3 前端
│   └── src/App.vue             # 聊天界面 + 业务对象侧边栏
├── start-all.ps1               # 一键启动全部服务
├── stop-all.ps1                # 一键停止全部服务
└── main.py                     # 客服后端入口
```

## 🔄 一条消息的旅程（架构）

```
用户输入（文本 / 订单卡片 / 商品卡片）
        │
        ▼
  chat_router (/api/chat)          ← FastAPI 路由，构建 UserMessage
        │
        ▼
  DialogueService                  ← 按 sender_id 加载 / 保存对话状态（MySQL）
        │
        ▼
  DialogueEngine.process_message
        │
        ├── 对象消息？─ 是 ─► 更新聚焦对象 → 尝试填槽 → 推进进行中流程
        │
        └── 文本消息 ─► TurnPlanner（LLM 意图识别，输出 TurnPlan JSON）
                            │
                            ▼
                     Validator 计划校验 ─ 不合法 ─► ClarifyResponder 澄清追问
                            │
                  ┌─────────┼──────────┐
                  ▼         ▼          ▼
              task 轨道  knowledge 轨道  chitchat 轨道
             流程引擎     Provider 检索   LLM 闲聊
             推进+Action  +LLM 生成回答
                  └─────────┼──────────┘
                            ▼
                     BotMessage 返回前端（支持 TTS / 复制）
```

## 🚀 快速开始

### 环境要求

- Python >= 3.12，[uv](https://docs.astral.sh/uv/)
- Node.js >= 18
- MySQL 8.x（本地运行，需手动建库）

### 1. 配置环境变量

在项目根目录创建 `.env`（已被 .gitignore 忽略，注意不要提交）：

```env
# 应用
APP_HOST=127.0.0.1
APP_PORT=18082

# MySQL
DATABASE_URL=mysql+aiomysql://root:你的密码@127.0.0.1:3306/customer_service?charset=utf8mb4

# LLM（任意 OpenAI 兼容接口）
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://xxx
LLM_MODEL=xxx

# 模拟电商后端地址
COMMERCE_API_BASE_URL=http://127.0.0.1:18081
```

### 2. 初始化数据库

```sql
CREATE DATABASE IF NOT EXISTS customer_service DEFAULT CHARSET utf8mb4;
```

首次启动会自动建表（`dialogue_states`，每个用户一行 JSON 状态）。

### 3. 一键启动

```powershell
# 项目根目录执行：启动 模拟电商后端(18081) + 客服后端(18082) + 前端(5173)
.\start-all.ps1

# 一键停止
.\stop-all.ps1
```

浏览器访问 <http://127.0.0.1:5173> 即可体验。

<details>
<summary>手动分别启动（Windows / Linux / Mac 通用）</summary>

```bash
# 模拟电商后端
cd ecommerce-service-backend && uv sync && uv run python main.py

# 客服后端
uv sync && python main.py

# 前端
cd customer-service-frontend && npm install && npm run dev
```
</details>

## 📡 API 概览

### `POST /api/chat` — 发送消息

```json
// 文本消息
{ "sender_id": "u1001", "text": "我要退款" }

// 对象消息（卡片）
{
  "sender_id": "u1001",
  "object": { "type": "order", "id": "A20260410001", "title": "iPhone 15 Pro", "attributes": { "status": "待发货" } }
}
```

响应：

```json
{
  "sender_id": "u1001",
  "messages": [ { "text": "请告诉我你的订单号。", "object": null } ]
}
```

### `GET /api/chat/history?sender_id=u1001` — 拉取历史

## 💡 设计亮点

1. **LLM 只当规划器，不当执行器**：意图识别结果必须经过 Validator 校验（意图注册表比对、槽位齐备性、对象类型匹配）才允许执行，从机制上防御幻觉
2. **Prompt 动态注入候选清单**：把知识意图注册表、流程清单序列化成 JSON 喂给模型，约束其只能从合法选项中选择
3. **意图 → 知识源的两级路由**：`KNOWLEDGE_INTENTS` 注册表把意图映射到多个 Provider（商品 API / 订单 API / FAQ / RAG），检索结果聚合成 Chunk 后统一交给 LLM 组织回答
4. **业务流程 YAML 化**：collect 步骤自动挂起为「系统流程」向用户追问，收集完成后自动回到用户主流程，类似 Rasa Forms 的机制
5. **依赖注入组装**：`builder.py` 统一装配引擎全部依赖，路由层通过 `Depends` 获取，模块间零硬编码单例

## 🗺️ Roadmap

- [ ] FAQ / RAG 知识库接入（当前为占位实现）
- [ ] 多流程并发与任务抢占恢复策略优化
- [ ] 对话数据分析看板
- [ ] 流式输出（SSE）支持

## ⚠️ 免责声明

本项目为个人学习作品，LLM 接口与电商后端均为演示用途，请勿直接用于生产环境。
