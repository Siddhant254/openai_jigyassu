from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True)
    password = Column(String)

    queries = relationship("Query", back_populates="user")

class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query_text = Column(String, index=True)
    file_name = Column(String, index=False)
    subject = Column(String, index=False)
    chapter = Column(String, index=False)

    user = relationship("User", back_populates="queries")  # Many-to-One Relationship


class Topics(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, index=False)
    chapters = Column(String, index=False)


class StudyMaterial(Base):
    __tablename__ = "study_materials"

    material_id = Column(String, primary_key=True, index=True)
    subject = Column(String)
    chapter = Column(String)
    file_path = Column(String)
    content = Column(String)