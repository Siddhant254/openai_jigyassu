from pydantic import BaseModel
from typing import List, Optional


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str

class UserCreate(UserBase):
    password: str
    confirm_password: str


class QueryResponse(BaseModel):
    id: int
    user_id: int
    query_text: str
    subject: str
    chapter: str
    file_name: str

    class Config:
        orm_mode = True

class QueryCreate(BaseModel):
    user_id: int
    query_text: str
    subject: str
    chapter: str
    file_name: str


class TopicsResponse(BaseModel):
    id: int
    subject: str
    chapters: str

    class Config:
        orm_mode = True

class TopicsCreate(BaseModel):
    subject: str
    chapters: str





class UserResponse(UserBase):
    id: int
    queries: List[QueryResponse] = []  # Include user's queries in the response 

    class Config:
        orm_mode = True

class StudyMaterialResponse(BaseModel):
    material_id: str
    subject: str
    chapter: str

    class Config:
        orm_mode = True

class UserBasicInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str

    class Config:
        orm_mode = True

