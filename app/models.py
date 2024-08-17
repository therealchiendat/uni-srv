from typing import Optional
from pydantic import BaseModel, Field
from datetime import date

class Course(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    university: str
    city: str
    country: str
    course_name: str
    course_description: str
    start_date: date
    end_date: date
    price: float
    currency: str
    
    class Config:
        allow_population_by_field_name = True  # Allows alias to be used in the output model