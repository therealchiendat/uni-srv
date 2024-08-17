from typing import List, Optional
from pymongo.errors import DuplicateKeyError
import pandas as pd
import io
from pymongo import MongoClient
from bson.objectid import ObjectId
from ..models import Course
from datetime import datetime, timedelta
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = MongoClient("mongodb://mongodb:27017/")
db = client.courses_db
expire_after_seconds = 600

def create_ttl_index():
    db.courses.create_index("created_at", expireAfterSeconds=expire_after_seconds)


def check_data_expiry():
    # Get the current time
    now = datetime.utcnow()

    # Check the latest document in the collection
    latest_doc = db.courses.find_one(sort=[("created_at", -1)])

    if latest_doc:
        data_age = now - latest_doc['created_at']

        # Check if the data is older than {expire_after_seconds} seconds
        if data_age.total_seconds() > expire_after_seconds:
            logger.info("Data expired, fetching new data...")
            load_and_store_data()
        else:
            logger.info("Data is fresh, no need to fetch new data.")
            logger.info("Data age: %s seconds", data_age.total_seconds())
    else:
        # If no documents exist, fetch new data
        logger.info("No data found, fetching new data...")
        load_and_store_data()


def map_mongo_to_course(doc):
    return Course(
        id=str(doc['_id']),
        university=doc.get('University', ''),
        city=doc.get('City', ''),
        country=doc.get('Country', ''),
        course_name=doc.get('CourseName', ''),
        course_description=doc.get('CourseDescription', ''),
        start_date=doc.get('StartDate'),
        end_date=doc.get('EndDate'),
        price=doc.get('Price', 0.0),
        currency=doc.get('Currency', '')
    )

def load_and_store_data():
    # Download the CSV file
    url = "https://api.mockaroo.com/api/501b2790?count=100&key=8683a1c0"
    response = requests.get(url)
    data = response.content.decode('utf-8')

    # Load data into a pandas DataFramt09011995D
    df = pd.read_csv(io.StringIO(data))

    # Normalize and add a created_at field
    df['created_at'] = datetime.utcnow()

    # Convert DataFrame to dictionary and insert into MongoDB
    try:
        db.courses.insert_many(df.to_dict('records'))
    except DuplicateKeyError:
        # Handle duplicate keys if necessary
        pass

def search_courses(
    search_term: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
) -> List[Course]:
    query = {}
    if search_term and isinstance(search_term, str):  # Ensure search_term is a string
        regex = {"$regex": search_term, "$options": "i"}
        query = {"$or": [
            {"University": regex},
            {"City": regex},
            {"Country": regex},
            {"CourseName": regex}
        ]}
    
    # Apply skip and limit for pagination
    docs = db.courses.find(query)
    
    # Map each document to a Course model
    courses = [map_mongo_to_course(doc) for doc in docs]
    
    return courses


def get_course_by_id(course_id: str) -> Course:
    try:
        doc = db.courses.find_one({"_id": ObjectId(course_id)})
        logger.info('Document: %s', doc)
        logger.info('Document mapping: %s', map_mongo_to_course(doc))
        return map_mongo_to_course(doc)
    except Exception as e:
        logger.error('Database query failed: %s', e)
        raise e

def get_all_courses(skip: int = 0, limit: int = 10) -> List[Course]:
    try:
        # Check if the data has expired
        check_data_expiry()

        # Apply skip and limit to the MongoDB query
        # docs = db.courses.find({}).skip(skip).limit(limit)
        docs = db.courses.find({}) 

        # Map each document to a Course model
        courses = [map_mongo_to_course(doc) for doc in docs]

        return courses
    except Exception as e:
        logger.error('Database query failed: %s', e)
        raise e

def create_course(course: Course) -> str:
    try:
        # Convert Course model to dictionary, ensuring the correct field names
        course_dict = {
            "University": course.university,
            "City": course.city,
            "Country": course.country,
            "CourseName": course.course_name,
            "CourseDescription": course.course_description,
            "StartDate": datetime.combine(course.start_date, datetime.min.time()),
            "EndDate": datetime.combine(course.end_date, datetime.min.time()),
            "Price": course.price,
            "Currency": course.currency,
            "created_at": datetime.utcnow()
        }

        result = db.courses.insert_one(course_dict)
        return str(result.inserted_id)
    except Exception as e:
        logger.error('Database insertion failed: %s', e)
        raise e
    
def update_course(course_id: str, updated_course: Course) -> bool:
    try:
        updated_course_dict = {
            "University": updated_course.university,
            "City": updated_course.city,
            "Country": updated_course.country,
            "CourseName": updated_course.course_name,
            "CourseDescription": updated_course.course_description,
            "StartDate": datetime.combine(updated_course.start_date, datetime.min.time()),
            "EndDate": datetime.combine(updated_course.end_date, datetime.min.time()),
            "Price": updated_course.price,
            "Currency": updated_course.currency
        }

        result = db.courses.update_one(
            {"_id": ObjectId(course_id)},
            {"$set": updated_course_dict}
        )
        return result.matched_count > 0
    except Exception as e:
        logger.error('Database update failed: %s', e)
        raise e

    
def delete_course(course_id: str) -> bool:
    try:
        result = db.courses.delete_one({"_id": ObjectId(course_id)})
        return result.deleted_count > 0
    except Exception as e:
        logger.error('Database deletion failed: %s', e)
        raise e