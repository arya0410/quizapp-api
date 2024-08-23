from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class ChoiceBase(BaseModel):
    choice_text: str
    is_correct: bool

class QuestionBase(BaseModel):
    question_text: str
    choices: List[ChoiceBase]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/questions/")
async def create_question(question: QuestionBase, db: Session = Depends(get_db)):
    # Create a new question instance
    db_question = models.Questions(question_text=question.question_text)
    
    # Add the question to the database
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    
    # Add choices associated with the question
    for choice in question.choices:
        db_choice = models.Choices(
            choice_text=choice.choice_text,
            is_correct=choice.is_correct,
            question_id=db_question.id
        )
        db.add(db_choice)
    
    # Commit the transaction after adding choices
    db.commit()
    
    return {"question_id": db_question.id}
