from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy import select
from core.database import Base
from modules.auth.domain.entities.entities import User, Role
from modules.auth.domain.repository import IAuthRepository


# ── Modelos ORM ───────────────────────────────────────────────────────────────
class RoleModel(Base):
    __tablename__ = "roles"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String(50), nullable=False, unique=True)
    description = Column(String(150), nullable=True)

    users = relationship("UserModel", back_populates="role")


class UserModel(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String(100), nullable=False)
    last_name  = Column(String(100), nullable=False)
    password   = Column(String(255), nullable=False)
    email      = Column(String(150), nullable=False, unique=True)
    role_id    = Column(Integer, ForeignKey("roles.id"), nullable=False, default=3)
    circuit_id = Column(Integer, ForeignKey("circuits.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    role    = relationship("RoleModel", back_populates="users")
    creator = relationship("UserModel", remote_side=[id])


# ── Repositorio ───────────────────────────────────────────────────────────────
class AuthRepository(IAuthRepository):

    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def get_user_by_email(self, email: str) -> User | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.role))
                .where(UserModel.email == email)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def get_user_by_id(self, user_id: int) -> User | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.role))
                .where(UserModel.id == user_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def create_user(
        self,
        name:       str,
        last_name:  str,
        email:      str,
        password:   str,
        role_id:    int,
        circuit_id: int | None = None,
    ) -> User:
        async with self._session_factory() as session:
            model = UserModel(
                name=name,
                last_name=last_name,
                email=email,
                password=password,
                role_id=role_id,
                circuit_id=circuit_id,
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)

            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.role))
                .where(UserModel.id == model.id)
            )
            model = result.scalar_one()
            return self._to_entity(model)

    def _to_entity(self, model: UserModel) -> User:
        role = None
        if model.role:
            role = Role(
                id=model.role.id,
                name=model.role.name,
                description=model.role.description,
            )
        return User(
            id=model.id,
            name=model.name,
            last_name=model.last_name,
            email=model.email,
            password=model.password,
            role_id=model.role_id,
            circuit_id=model.circuit_id,
            role=role,
            created_by=model.created_by,
        )