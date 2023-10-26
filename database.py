from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
import os


# Rest of your code remains the same

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

def load_carousel_courses_from_db(student_number):
  with engine.connect() as conn:
      query = text("""
          SELECT c.*, IFNULL(r.rating, 0) AS favorite
          FROM courses c
          LEFT JOIN r_favorites r ON c.course_code = r.course_code 
              AND r.student_number = :student_number
          WHERE c.site_placement = 'Carousel'
      """)
      carousel_courses = []
      for row in conn.execute(query, {"student_number": student_number}):
          result_dict = row._asdict()  # Convert the row to a dictionary
          carousel_courses.append(result_dict)
      return carousel_courses



def load_best_courses_from_db(student_number):
  with engine.connect() as conn:
    query = text("""
        SELECT c.*, IFNULL(r.rating, 0) AS favorite
        FROM courses c
        LEFT JOIN r_favorites r ON c.course_code = r.course_code 
            AND r.student_number = :student_number
        WHERE c.site_placement = 'Best'
    """)
    best_courses = []
    for row in conn.execute(query, {"student_number": student_number}):
        result_dict = row._asdict()  # Convert the row to a dictionary
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

def load_favorite_courses_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM courses WHERE favorite = 1"))
        favorite_courses = []
        columns = result.keys()
        for row in result:
            result_dict = {column: value for column, value in zip(columns, row)}
            favorite_courses.append(result_dict)
        return favorite_courses


def add_rating_to_db(course_code, student_number, data):
  with engine.connect() as conn:
      conn.execute(
          text("INSERT INTO r_favorites (course_code, student_number, rating) VALUES (:course_code, :student_number, :rating)"),
          {"course_code": course_code, "student_number": student_number, "rating": data['favorite']}
      )

def remove_rating_from_db(course_code, student_number):
  with engine.connect() as conn:
      conn.execute(
          text("UPDATE r_favorites SET favorite = 0 WHERE course_code = :course_code AND student_number = :student_number"),
          {"course_code": course_code, "student_number": student_number}
      )



def add_login_to_db(student_number, password):
  with engine.connect() as conn:
      conn.execute(
          text("INSERT INTO r_users (student_number, password) VALUES (:student_number, :password)"),
          {"student_number": student_number, "password": password}
      )

def check_credentials(student_number, password):
  with engine.connect() as conn:
      result = conn.execute(
          text("SELECT * FROM r_users WHERE student_number = :student_number AND password = :password"),
          {"student_number": student_number, "password": password}
      )
      return result.fetchone() is not None

def add_interests_to_db(data):
  with engine.connect() as conn:
      query = text("INSERT INTO r_users (marketing, economics, management, sustainability, biology, politics, law, communication, Bachelor, Master) "
                   "VALUES (:marketing, :economics, :management, :sustainability, :biology, :politics, :law, :communication, :Bachelor, :Master)")

      # Construct the parameter dictionary
      params = {
          'marketing': data.get('marketing'),
          'economics': data.get('economics'),
          'management': data.get('management'),
          'sustainability': data.get('sustainability'),
          'biology': data.get('biology'),
          'politics': data.get('politics'),
          'law': data.get('law'),
          'communication': data.get('communication'),
          'Bachelor': data.get('Bachelor'),
          'Master': data.get('Master')
      }

      conn.execute(query, params)


def update_interests(student_number, password, data):
  with engine.connect() as conn:
      query = text(
          "UPDATE r_users SET "
          "marketing = :marketing, "
          "economics = :economics, "
          "management = :management, "
          "sustainability = :sustainability, "
          "biology = :biology, "
          "politics = :politics, "
          "law = :law, "
          "communication = :communication, "
          "Bachelor = :Bachelor, "
          "Master = :Master "
              "WHERE student_number = :student_number AND password = :password"
          )
# Add student_number and password to the parameter dictionary
      params = {
          'marketing': data.get('marketing'),
          'economics': data.get('economics'),
          'management': data.get('management'),
          'sustainability': data.get('sustainability'),
          'biology': data.get('biology'),
          'politics': data.get('politics'),
          'law': data.get('law'),
          'communication': data.get('communication'),
          'Bachelor': data.get('Bachelor'),
          'Master': data.get('Master'),
          'student_number': student_number,
          'password': password
      }

      conn.execute(query, params)



def add_views_to_db(student_number, course_code, timestamp):
  with engine.connect() as conn:
      query = text("INSERT INTO course_views (student_number, course_code, timestamp) VALUES (:student_number, :course_code, :timestamp)")
      conn.execute(query, {"student_number": student_number, "course_code": course_code, "timestamp": timestamp})




