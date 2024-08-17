import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.crud.course_crud import create_ttl_index, check_data_expiry
from .routes import courses

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(courses.router)

@app.on_event("startup")
def startup_event():
    create_ttl_index()
    check_data_expiry()

@app.get("/")
def read_root():
    return {"message": "Welcome to the University Course API"}

if __name__ == "__main__":
    uvicorn.run(app, port=8000, host='0.0.0.0', reload=True)