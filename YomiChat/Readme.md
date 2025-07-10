# 🧠 Chat Agent Web Service

一个基于多智能体框架的交互式聊天系统，后端使用 **FastAPI**，前端使用 **React + JavaScript** 实现时尚风格的 Web 聊天界面。

## 📌 项目简介

本项目集成了：

- 多智能体架构：SmolAgents + ToolCallingAgent + ManagedAgent + CodeAgent
- 后端 API 提供 agent 服务，支持 Markdown 输出
- 前端聊天 UI，支持多行输入、头像展示、实时 Markdown 渲染

---

## 🧰 技术栈

| 模块   | 技术      |
|--------|-----------|
| 前端   | React + react-markdown + CSS |
| 后端   | FastAPI + SmolAgents + LiteLLM |
| 网络通讯 | REST API （POST `/chat`） |
| 工具链 | DuckDuckGo Search + JinaAI 页面爬取 |

---

## 🚀 启动方法

### 🔙 后端 FastAPI

#### ✅ 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

#### ▶️ 启动服务
uvicorn main:app --reload --port 8000

### 🔜 前端 React
#### ✅ 安装依赖
```bash
cd frontend
npm install
npm start
```