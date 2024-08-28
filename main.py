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

    class Config:
        orm_mode = True

class QuestionCreate(BaseModel):
    question_text: str
    choices: List[ChoiceBase]

    class Config:
        orm_mode = True

class QuestionResponse(BaseModel):
    id: int
    question_text: str
    choices: List[ChoiceBase] = []  

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/questions/", response_model=QuestionResponse)
async def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    db_question = models.Questions(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    for choice in question.choices:
        db_choice = models.Choices(
            choice_text=choice.choice_text,
            is_correct=choice.is_correct,
            question_id=db_question.id
        )
        db.add(db_choice)
    
    db.commit()

    return {"id": db_question.id, "question_text": db_question.question_text, "choices": question.choices}

@app.get("/questions/{question_id}", response_model=QuestionResponse)
async def read_question(question_id: int, db: Session = Depends(get_db)):
    db_question = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    
    choices = db.query(models.Choices).filter(models.Choices.question_id == question_id).all()
    return {"id": db_question.id, "question_text": db_question.question_text, "choices": [{"choice_text": choice.choice_text, "is_correct": choice.is_correct} for choice in choices]}

@app.get("/questions/", response_model=List[QuestionResponse])
async def read_questions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    db_questions = db.query(models.Questions).offset(skip).limit(limit).all()
    result = []
    for question in db_questions:
        choices = db.query(models.Choices).filter(models.Choices.question_id == question.id).all()
        result.append({
            "id": question.id,
            "question_text": question.question_text,
            "choices": [{"choice_text": choice.choice_text, "is_correct": choice.is_correct} for choice in choices]
        })
    return result

@app.put("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(question_id: int, question: QuestionCreate, db: Session = Depends(get_db)):
    db_question = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    
    db_question.question_text = question.question_text
    db.query(models.Choices).filter(models.Choices.question_id == question_id).delete()
    
    for choice in question.choices:
        db_choice = models.Choices(
            choice_text=choice.choice_text,
            is_correct=choice.is_correct,
            question_id=db_question.id
        )
        db.add(db_choice)
    
    db.commit()

    choices = db.query(models.Choices).filter(models.Choices.question_id == question_id).all()
    return {"id": db_question.id, "question_text": db_question.question_text, "choices": [{"choice_text": choice.choice_text, "is_correct": choice.is_correct} for choice in choices]}

@app.delete("/questions/{question_id}", status_code=204)
async def delete_question(question_id: int, db: Session = Depends(get_db)):
    db_question = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    
    db.query(models.Choices).filter(models.Choices.question_id == question_id).delete()
    db.delete(db_question)
    db.commit()
    
    return None
