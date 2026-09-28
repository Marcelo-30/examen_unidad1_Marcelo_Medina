from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Laptop(Base):
    __tablename__ = "laptops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    marca: Mapped[str] = mapped_column(String(100), nullable=False)
    modelo: Mapped[str] = mapped_column(String(100), nullable=False)
    ram_gb: Mapped[int] = mapped_column(Integer, nullable=False)
    disponible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
