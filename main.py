from fastapi import FastAPI
from api.practice import router as practice_router
from api.coding_exercise import router as coding_router
from api.suggestions import router as suggestions_router
from api.submit import router as submit_router
from api.generate_questions import router as questions_router
from api.generate_answers import router as answers_router
from api.compare_answers import router as compare_answers_routers
from fastapi.middleware.cors import CORSMiddleware
from utils.vector_store import init_faiss
app = FastAPI()

# Initialize FAISS on app startup
@app.on_event("startup")
async def startup():
    init_faiss()
#  Add CORS middleware to the main FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      
    allow_credentials=True,
    allow_methods=["*"],       
    allow_headers=["*"],       
)

# Register routers
app.include_router(practice_router, prefix="/api")
app.include_router(coding_router, prefix="/api")
app.include_router(suggestions_router, prefix="/api")
app.include_router(submit_router,prefix="/api")
app.include_router(questions_router,prefix="/api")
app.include_router(answers_router,prefix="/api")
app.include_router(compare_answers_routers,prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
