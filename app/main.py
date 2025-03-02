from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

# Obtener la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://luis:123@db:5432/penjat")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    total_games = Column(Integer, default=0)
    total_wins = Column(Integer, default=0)
    max_score = Column(Integer, default=0)

class Word(Base):
    __tablename__ = "words"
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, index=True)
    theme = Column(String)

class GameLog(Base):
    __tablename__ = "game_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    word_id = Column(Integer, ForeignKey("words.id"))
    attempts = Column(Integer)
    errors = Column(Integer)
    score = Column(Integer)
    finished = Column(Boolean)

class UIText(Base):
    __tablename__ = "ui_texts"
    id = Column(Integer, primary_key=True, index=True)
    screen = Column(String)
    text = Column(String)

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Esquemas Pydantic
class UserCreate(BaseModel):
    username: str
    password_hash: str

class WordCreate(BaseModel):
    word: str
    theme: str

class GameLogCreate(BaseModel):
    user_id: int
    word_id: int
    attempts: int
    errors: int
    score: int
    finished: bool

class UITextCreate(BaseModel):
    screen: str
    text: str

# FastAPI App
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rutas para usuarios
@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username, password_hash=user.password_hash)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Rutas para palabras
@app.post("/words/")
def create_word(word: WordCreate, db: Session = Depends(get_db)):
    db_word = Word(word=word.word, theme=word.theme)
    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return db_word

# Rutas para registros de juego
@app.post("/game_logs/")
def create_game_log(game_log: GameLogCreate, db: Session = Depends(get_db)):
    db_log = GameLog(**game_log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# Rutas para textos de UI
@app.post("/ui_texts/")
def create_ui_text(ui_text: UITextCreate, db: Session = Depends(get_db)):
    db_text = UIText(screen=ui_text.screen, text=ui_text.text)
    db.add(db_text)
    db.commit()
    db.refresh(db_text)
    return db_text