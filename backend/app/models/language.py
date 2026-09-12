from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Language(Base):
    __tablename__ = "languages"

    code: Mapped[str] = mapped_column(String(10), primary_key=True)  # "en", "hi", ...
    name: Mapped[str] = mapped_column(String(50), nullable=False)  # "Hindi"
    native_name: Mapped[str] = mapped_column(String(50), nullable=False)  # "हिन्दी"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
