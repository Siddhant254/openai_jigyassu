from fastapi import APIRouter, FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from models import models
from schemas import schemas
from db.database import SessionLocal, engine
from utils.password import hash_password,verify_password

# Create database tables
models.Base.metadata.create_all(bind=engine)

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Signup Route
@router.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = hash_password(user.password)

    new_user = models.User(
        first_name = user.first_name,
        last_name = user.last_name,
        email = user.email,
        phone_number = user.phone_number,
        password = hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Login Route
@router.post("/login", response_model = schemas.UserResponse)
def login(email: str = Form(...),password: str = Form(...),db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    return {"message": "Login Successful", "user_id": user.id }



# # Create a new user
# @router.post("/user", response_model=schemas.UserResponse)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = models.User(name=user.name, email=user.email)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

# # Get a user (with their queries)
# @router.get("/user/{user_id}", response_model=schemas.UserResponse)
# def get_user(user_id: int, db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.id == int(user_id)).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user


# # Get all queries for a user
# @router.get("/user/query", response_model=list[schemas.QueryResponse])
# def get_queries(db: Session = Depends(get_db)):
#     user_id = 1
#     querys = db.query(models.Query).filter(models.Query.user_id == int(user_id))
#     if not querys:
#         raise HTTPException(status_code=404, detail="Not found any Querys")
    
#     return querys

# @router.post("/user/query", response_model=list[schemas.QueryResponse])
# async def get_user_query(
#     query_text: str = Form(...),
#     subject: str = Form(...),
#     chapter: str = Form(...),
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db)
# ):
#     content = await file.read()
#     user_id = 1
#     db_query = models.Query(query_text=query_text, file_name=file.filename, subject=subject, chapter=chapter, user_id=int(user_id))
#     db.add(db_query)
#     db.commit()
#     db.refresh(db_query)
#     return [db_query]

# @router.get("/retreive-topic", response_model=list[schemas.TopicsResponse])
# def get_queries(db: Session = Depends(get_db)):
#     topics = db.query(models.Topics).filter()
#     if not topics:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     return topics

# @router.post("/create-topic", response_model=schemas.TopicsCreate)
# def create_topic(topic: schemas.TopicsCreate, db: Session = Depends(get_db)):
#     db_topic = models.Topics(subject=topic.subject, chapters=topic.chapters)
#     db.add(db_topic)
#     db.commit()
#     db.refresh(db_topic)
#     return db_topic