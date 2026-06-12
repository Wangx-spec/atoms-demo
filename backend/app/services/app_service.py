from uuid import UUID

from fastapi import HTTPException, status

from app.models.entities import GeneratedApp, User
from app.schemas.apps import GeneratedAppResponse, SaveGeneratedAppRequest
from app.services.repository import repository


class AppService:
    def save_app(self, user: User, payload: SaveGeneratedAppRequest) -> GeneratedAppResponse:
        generated = repository.add_app(
            GeneratedApp(
                user_id=user.id,
                session_id=payload.session_id,
                prompt=payload.prompt,
                html=payload.html,
                css=payload.css,
                js=payload.js,
                status=payload.status,
            )
        )
        return GeneratedAppResponse.model_validate(generated, from_attributes=True)

    def list_apps(self, user: User) -> list[GeneratedAppResponse]:
        return [
            GeneratedAppResponse.model_validate(app, from_attributes=True)
            for app in repository.list_apps(user.id)
        ]

    def get_app(self, user: User, app_id: UUID) -> GeneratedAppResponse:
        app = repository.get_app(app_id)
        if not app or app.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="App not found")
        return GeneratedAppResponse.model_validate(app, from_attributes=True)


app_service = AppService()
