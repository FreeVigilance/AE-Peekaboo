from src.infrastructure.models.public import User
from src.infrastructure.repositories.base import BaseRepository


class UserRepo(BaseRepository):
    """Репозиторий для работы с таблицей user в БД."""

    table = User
