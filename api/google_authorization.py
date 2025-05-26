from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from auth.google_auth import oauth
from db.database import SessionLocal, engine
from models import models
from sqlalchemy.orm import Session
from utils.password import verify_password

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create database tables
models.Base.metadata.create_all(bind=engine)

@router.get("/auth/google/login")
async def login_via_google(request: Request):
    redirect_uri = request.url_for('auth_via_google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/google/callback")
async def auth_via_google_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.parse_id_token(request, token)
    
    # Save or find user in DB
    email = user_info.get("email")
    name = user_info.get("name")

    # Example: Check if user exists, else create
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        user = models.User(email=email, first_name=name)
        db.add(user)
        db.commit()

    return {"message": "Login successful", "email": email, "name": name}
