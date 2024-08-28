from pydantic import BaseModel
from typing import List

class ChoiceBase(BaseModel):
    choice_text: str
    is_correct: bool

    class Config:
        orm_mode = True

class QuestionCreate(BaseModel):
    question_text: str
    choices: List[ChoiceBase]

class QuestionResponse(BaseModel):
    id: int
    question_text: str
    choices: List[ChoiceBase] = []  

    class Config:
        orm_mode = True
