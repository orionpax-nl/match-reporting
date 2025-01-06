from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

app = FastAPI()

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True)
    team_home = Column(String)
    team_away = Column(String)
    goals = relationship("Goal", back_populates="match")

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    player = Column(String)
    time = Column(String)
    match = relationship("Match", back_populates="goals")

Base.metadata.create_all(bind=engine)

class GoalCreate(BaseModel):
    player: str
    time: str

@app.post("/matches/{match_id}/goals")
def register_goal(match_id: int, goal: GoalCreate):
    db = SessionLocal()
    match = db.query(Match).filter(Match.id == match_id).first()
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    db_goal = Goal(match_id=match_id, player=goal.player, time=goal.time)
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal
