from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
from models import Laptop


class LaptopCreate(BaseModel):
    marca: str
    modelo: str
    ram_gb: int = Field(gt=0)


class LaptopResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    marca: str
    modelo: str
    ram_gb: int
    disponible: bool


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.scalar(select(Laptop.id).limit(1)) is None:
            db.add_all(
                [
                    Laptop(marca="Dell", modelo="Latitude 5440", ram_gb=16, disponible=True),
                    Laptop(marca="Lenovo", modelo="ThinkPad E14", ram_gb=8, disponible=False),
                    Laptop(marca="HP", modelo="ProBook 450", ram_gb=16, disponible=True),
                ]
            )
            db.commit()
    yield


app = FastAPI(lifespan=lifespan)


def get_db():
    with SessionLocal() as db:
        yield db


@app.get("/")
def inicio():
    return {"mensaje": "API del laboratorio de cómputo"}


@app.get("/laptops", response_model=list[LaptopResponse])
def listar_laptops(db: Session = Depends(get_db)):
    return db.scalars(select(Laptop).order_by(Laptop.id)).all()


@app.get("/laptops/disponibles", response_model=list[LaptopResponse])
def listar_disponibles(db: Session = Depends(get_db)):
    return db.scalars(
        select(Laptop).where(Laptop.disponible.is_(True)).order_by(Laptop.id)
    ).all()


@app.get("/laptops/{laptop_id}", response_model=LaptopResponse)
def obtener_laptop(laptop_id: int, db: Session = Depends(get_db)):
    laptop = db.get(Laptop, laptop_id)
    if laptop is None:
        raise HTTPException(status_code=404, detail="Laptop no encontrada")
    return laptop


@app.post("/laptops", response_model=LaptopResponse)
def crear_laptop(datos: LaptopCreate, db: Session = Depends(get_db)):
    laptop = Laptop(**datos.model_dump(), disponible=True)
    db.add(laptop)
    db.commit()
    db.refresh(laptop)
    return laptop
