from app.workers.celery_app import celery_app


if celery_app:

    @celery_app.task(name="generate_multimodal_asset")
    def generate_multimodal_asset(prompt: str, asset_type: str) -> dict[str, str]:
        return {"prompt": prompt, "type": asset_type, "status": "mocked"}
