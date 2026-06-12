from uuid import UUID

from app.models.entities import AgentSession, GeneratedApp, Task, User


class InMemoryRepository:
    """Development repository. Replace with SQLAlchemy repositories in production."""

    def __init__(self) -> None:
        self.users: dict[UUID, User] = {}
        self.users_by_email: dict[str, UUID] = {}
        self.sessions: dict[UUID, AgentSession] = {}
        self.apps: dict[UUID, GeneratedApp] = {}
        self.tasks: dict[UUID, Task] = {}

    def add_user(self, user: User) -> User:
        self.users[user.id] = user
        self.users_by_email[user.email] = user.id
        return user

    def get_user(self, user_id: UUID) -> User | None:
        return self.users.get(user_id)

    def get_user_by_email(self, email: str) -> User | None:
        user_id = self.users_by_email.get(email)
        return self.users.get(user_id) if user_id else None

    def add_session(self, session: AgentSession) -> AgentSession:
        self.sessions[session.id] = session
        return session

    def get_session(self, session_id: UUID) -> AgentSession | None:
        return self.sessions.get(session_id)

    def add_app(self, app: GeneratedApp) -> GeneratedApp:
        self.apps[app.id] = app
        return app

    def list_apps(self, user_id: UUID) -> list[GeneratedApp]:
        return [app for app in self.apps.values() if app.user_id == user_id]

    def get_app(self, app_id: UUID) -> GeneratedApp | None:
        return self.apps.get(app_id)

    def add_task(self, task: Task) -> Task:
        self.tasks[task.id] = task
        return task

    def get_task(self, task_id: UUID) -> Task | None:
        return self.tasks.get(task_id)


repository = InMemoryRepository()
