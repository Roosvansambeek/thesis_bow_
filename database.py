from sqlalchemy import create_engine
from sqlalchemy import text
import os

db_connection_string = os.environ['DB_CONNECTION_STRING']

engine = create_engine(
  db_connection_string,
  connect_args={
    "ssl": {
      "ssl_ca": "/etc/ssl/cert.pem"
    }
  }
)

def load_courses_from_db():
  with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM courses"))
    courses = []
    columns = result.keys()
    for row in result:
      result_dict = {column: value for column, value in zip(columns, row)}
      courses.append(result_dict)
    return courses

def load_course_from_db(course_code):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM courses WHERE course_code = :val"), parameters=dict(val=course_code))
        course = []
        columns = result.keys()
        for row in result:
            result_dict = {column: value for column, value in zip(columns, row)}
            if len(row) == 0:
                return None
            else:
                return result_dict

def load_carousel_courses_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM courses WHERE site_placement = 'Carousel'"))
        carousel_courses = []
        columns = result.keys()
        for row in result:
            result_dict = {column: value for column, value in zip(columns, row)}
            carousel_courses.append(result_dict)
        return carousel_courses

def load_best_courses_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM courses WHERE site_placement = 'Best'"))
        best_courses = []
        columns = result.keys()
        for row in result:
            result_dict = {column: value for column, value in zip(columns, row)}
            best_courses.append(result_dict)
        return best_courses

def load_explore_courses_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM courses WHERE site_placement = 'Explore'"))
        explore_courses = []
        columns = result.keys()
        for row in result:
            result_dict = {column: value for column, value in zip(columns, row)}
            explore_courses.append(result_dict)
        return explore_courses

def load_compulsory_courses_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM courses WHERE site_placement = 'Compulsory'"))
        compulsory_courses = []
        columns = result.keys()
        for row in result:
            result_dict = {column: value for column, value in zip(columns, row)}
            compulsory_courses.append(result_dict)
        return compulsory_courses

def get_rating_from_db(course_code):
    with engine.connect() as conn:
        query = text("SELECT rating FROM ratings WHERE course_code = :val")
        result = conn.execute(query, {"val": course_code})
        rating_row = result.fetchone()
        if rating_row is not None:
            rating = rating_row[0]
            return rating
        else:
            return None

def add_rating_to_db(course_code, data):
    with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO ratings (course_code, rating) VALUES (:course_code, :rating)"),
                {"course_code": course_code, "rating": data['favorite']}
            )

def remove_rating_from_db(course_code):
    with engine.connect() as conn:
        conn.execute(
            text("DELETE FROM ratings WHERE course_code = :course_code"),
            {"course_code": course_code}
        )







