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

def get_rating_from_db(course_code):
    with engine.connect() as conn:
        query = text("SELECT favorite FROM courses WHERE course_code = :val")
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
                text("UPDATE courses SET favorite = :rating WHERE course_code = :course_code"),
                {"course_code": course_code, "rating": data['favorite']}
            )

def remove_rating_from_db(course_code, data):
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE courses SET favorite = DEFAULT WHERE course_code = :course_code"),
            {"course_code": course_code}
        )







