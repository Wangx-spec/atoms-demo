# Atoms Demo

## 项目介绍

Atoms Demo 是一个 AI 创作平台示例项目，用户可以用自然语言生成、编辑、预览和保存 Web 应用原型，并进一步使用多模态创作、作品社区、语义搜索、代码沙箱、积分和管理后台等能力。

## 技术栈

- 后端：FastAPI、SQLAlchemy async、Alembic、PostgreSQL、JWT、LangGraph、Celery、Redis、MinIO、Qdrant、Docker SDK。
- 前端：Vue 3、TypeScript、Vite、Pinia、Vue Router、Axios。
- 基础设施：Docker Compose、本地 Nginx 配置、Kubernetes/Helm/CI/监控脚手架。

## 启动方式

启动前请先复制环境变量模板，并按需填写本地配置：

```bash
cp backend/.env.example backend/.env
```

推荐使用 Docker Compose 启动完整本地环境：

```bash
cd infra
docker compose up --build
```

如果需要手动执行数据库迁移：

```bash
cd infra
docker compose run --rm backend python -m alembic upgrade head
```

启动完成后访问：

- 前端：http://localhost:5173
- 后端 API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/health
