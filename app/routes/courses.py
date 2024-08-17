from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from ..models import Course
from ..crud.course_crud import create_course, delete_course, get_total_courses, search_courses, update_course, get_all_courses, get_course_by_id
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/courses/", response_model=List[Course])
def get_courses(
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
):
    logger.info('Searching for courses...')
    logger.info('Search term: %s', search)
    courses = search_courses(search, skip, limit)
    return courses



@router.get("/courses/all", response_model=List[Course])
def get_all(skip: int = 0, limit: int = 10):
    try:
        courses = get_all_courses(skip, limit)
        return courses
    except Exception as e:
        logger.error('Error retrieving all courses: %s', e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    
@router.get("/courses/total", response_model=int)
def get_total():
    try:
        total = get_total_courses()
        return total
    except Exception as e:
        logger.error('Error retrieving total courses: %s', e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    
@router.get("/courses/{course_id}", response_model=Course)
def get_course(course_id: str):
    try:
        course = get_course_by_id(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
    except Exception as e:
        logger.error('Error retrieving course: %s', e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    
    return course


@router.post("/courses/", response_model=Course, status_code=status.HTTP_201_CREATED)
def create(course: Course):
    logger.info('Creating course...')
    logger.info('Course: %s', course)
    try:
        logger.info('Attempting to create course in the database...')
        course_id = create_course(course)
        logger.info('Course created with ID: %s', course_id)
        course.id = course_id
    except Exception as e:
        logger.error('Error creating course: %s', e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    
    return course

@router.put("/courses/{course_id}", response_model=Course)
def update(course_id: str, updated_course: Course):
    try:
        success = update_course(course_id, updated_course)
        if not success:
            raise HTTPException(status_code=404, detail="Course not found")
    except Exception as e:
        logger.error('Error updating course: %s', e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    
    return updated_course

@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(course_id: str):
    try:
        success = delete_course(course_id)
        if not success:
            raise HTTPException(status_code=404, detail="Course not found")
    except Exception as e:
        logger.error('Error deleting course: %s', e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
