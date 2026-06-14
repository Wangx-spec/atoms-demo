from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- Core ---
    app_name: str = "Atoms Demo API"
    app_version: str = "0.1.0"
    api_secret_key: str = Field(default="change-me-in-production")
    access_token_expire_minutes: int = 60 * 24
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    database_url: str = "postgresql+asyncpg://atoms:atoms@localhost:5432/atoms_demo"

    # --- Stage 3: LLM providers ---
    # One of: deepseek | qwen | mock. Defaults to deepseek; set to mock for keyless local dev.
    llm_provider: str = "deepseek"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"
    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_model: str = "qwen-plus"
    llm_request_timeout: int = 120

    # --- Stage 4: async tasks / queue / object storage ---
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    image_provider: str = "mock"  # mock | qwen | comfyui | stablediffusion
    music_provider: str = "mock"  # mock | suno | musicgen | riffusion
    comfyui_base_url: str = ""
    stablediffusion_base_url: str = ""
    suno_api_key: str = ""
    minio_endpoint: str = "localhost:9000"
    # Browser-reachable endpoint used only to sign presigned GET URLs. In Docker
    # the internal endpoint is ``minio:9000`` while the browser must hit the host
    # mapped port, e.g. ``localhost:9100``.
    minio_public_endpoint: str = "localhost:9100"
    minio_access_key: str = "atoms"
    minio_secret_key: str = "atoms123456"
    minio_bucket: str = "atoms-artifacts"
    minio_secure: bool = False
    # Explicit region so presigned-URL signing stays fully offline (otherwise
    # minio-py issues a GetBucketLocation network call against the endpoint,
    # which hangs when the public endpoint is unreachable from the server).
    minio_region: str = "us-east-1"
    public_media_base_url: str = "http://localhost:9100"
    qwen_image_model: str = "wanx2.1-t2i-turbo"
    musicgen_base_url: str = ""

    # --- Stage 5: code sandbox ---
    sandbox_enabled: bool = True
    sandbox_static_image: str = "nginx:1.27-alpine"
    sandbox_node_image: str = "node:20-alpine"
    sandbox_python_image: str = "python:3.11-slim"
    sandbox_mem_limit: str = "512m"
    sandbox_cpus: float = 0.5
    sandbox_network_disabled: bool = True
    sandbox_timeout_seconds: int = 600
    sandbox_port_start: int = 18000
    sandbox_port_end: int = 18100
    sandbox_public_host: str = "localhost"

    # --- Stage 7: vector search / embeddings ---
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "artworks"
    embedding_provider: str = "mock"  # mock | qwen
    embedding_dim: int = 1024

    # --- Stage 8: security / observability ---
    rate_limit_default: str = "120/minute"
    rate_limit_generate: str = "20/minute"
    max_upload_mb: int = 10
    enable_metrics: bool = False
    enable_tracing: bool = False
    otel_exporter_endpoint: str = ""

    # --- Stage 9: billing / admin / payments ---
    admin_emails: list[str] = []
    credit_cost_code: int = 1
    credit_cost_image: int = 5
    credit_cost_music: int = 10
    stripe_api_key: str = ""
    stripe_webhook_secret: str = ""
    wechat_pay_key: str = ""
    alipay_app_id: str = ""
    alipay_private_key: str = ""


settings = Settings()
