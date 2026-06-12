# Atoms Demo

Atoms Demo 是一个 AI 创作平台的 MVP 骨架。它基于 `/Users/aimiaomiao/Downloads/项目方案.md` 中的项目方案，并从最小可用闭环开始：

1. 创建带 JWT 鉴权的演示用户。
2. 创建智能体会话。
3. 通过 SSE 流式返回模拟生成进度。
4. 生成可编辑的 HTML/CSS/JS。
5. 在沙箱 iframe 中预览结果。
6. 保存生成的应用。

## 技术栈

- 后端：FastAPI、Pydantic、JWT 鉴权、可替换的服务层。
- 前端：Vue 3、TypeScript、Vite、Pinia、Axios。
- 基础设施：Docker Compose，以及 PostgreSQL、Redis、MinIO 的占位配置。

## 项目结构

```txt
backend/
  app/
    api/routes/      FastAPI 路由模块
    agents/          为 LangGraph 预留的智能体图占位
    core/            配置和安全辅助工具
    models/          领域实体
    schemas/         请求/响应模型
    services/        鉴权、智能体、代码生成和应用服务
    workers/         为 Celery 预留的任务占位
frontend/
  src/
    api/             HTTP 客户端
    components/      工作区 UI
    stores/          Pinia 状态
    views/           页面视图
infra/
  docker-compose.yml
docs/
  implementation-plan.md
```

## 本地开发

### 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

API 文档：

- Swagger UI: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/health

### 前端

```bash
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173。

前端会自动创建或登录本地演示账号：

- 邮箱：`demo@atoms.local`
- 密码：`demo123456`

### Docker Compose

```bash
cd infra
docker compose up --build
```

## 当前说明

- 后端当前使用内存存储，便于快速迭代。重启后端会清空用户、会话和已保存的应用。
- `LLMProvider` 当前使用 `MockLLMProvider`。可以在 `backend/app/services/llm_service.py` 中添加 DeepSeek/Qwen Provider。
- Celery、PostgreSQL、Redis 和 MinIO 已作为下一步生产化改造的脚手架预留。
- MVP 阶段的代码编辑器使用 textarea 控件。核心 API 稳定后，可将 `CodeEditor.vue` 替换为 Monaco Editor。
