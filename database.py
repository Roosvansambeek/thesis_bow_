from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
import os
from algorithm import get_recommendations

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
    result = conn.execute(text("SELECT * FROM r_courses"))
    courses = []
    columns = result.keys()
    for row in result:
      result_dict = {column: value for column, value in zip(columns, row)}
      courses.append(result_dict)
    return courses


def load_carousel_courses_from_db(student_number):
  with engine.connect() as conn:
      query = text("""
          SELECT c.*, rf.rating 
          FROM r_courses c
          LEFT JOIN r_favorites4 rf
          ON c.course_code = rf.course_code AND rf.student_number = :student_number
      """)

      result = conn.execute(query, {"student_number": student_number})

      carousel_courses = []
      columns = result.keys()
      for row in result:
          result_dict = {column: value for column, value in zip(columns, row)}
          carousel_courses.append(result_dict)

      return carousel_courses


def load_best_courses_with_favorite_from_db(student_number):
  with engine.connect() as conn:
      query = text("""
          SELECT c.*, rf.rating 
          FROM r_courses c
          LEFT JOIN r_favorites4 rf
          ON c.course_code = rf.course_code AND rf.student_number = :student_number
      """)
    
      result = conn.execute(query, {"student_number": student_number})

      best_courses = []
      columns = result.keys()
      for row in result:
          result_dict = {column: value for column, value in zip(columns, row)}
          best_courses.append(result_dict)

      return best_courses






def add_test_to_db(request, student_number, course_code, favorite_value):
  with engine.connect() as conn:
      # Check if the record already exists
      existing_record = conn.execute(
          text("SELECT * FROM r_favorites4 WHERE course_code = :course_code AND student_number = :student_number"),
          {"course_code": course_code, "student_number": student_number}
      ).fetchone()

      # Fetch the 'id' from 'course_info' based on the 'course_code'
      course_info_id = conn.execute(
          text("SELECT id FROM r_courses WHERE course_code = :course_code"),
          {"course_code": course_code}
      ).fetchone()

      if course_info_id:
          course_info_id = course_info_id[0]
      else:
          # Handle the case where 'course_code' doesn't exist in 'course_info'
          # You can raise an exception, return an error, or handle it as needed
          # For now, I'm assuming you want to set it to NULL
          course_info_id = None

      print(f"Retrieved id for course_code={course_code}: id={course_info_id}")

      if existing_record:
          # Update the existing record
          query = text("UPDATE r_favorites4 SET rating = :rating, id = :id WHERE course_code = :course_code AND student_number = :student_number")
      else:
          # Insert a new record
          query = text("INSERT INTO r_favorites4 (course_code, student_number, rating, id) VALUES (:course_code, :student_number, :rating, :id)")

      conn.execute(query, {"course_code": course_code, "student_number": student_number, "rating": favorite_value, "id": course_info_id})



def load_favorite_courses_from_db(student_number):
    with engine.connect() as conn:
      query = text(""" 
          SELECT rf.*, c.course_code, c.course_name, c.content
          FROM r_courses c
          LEFT JOIN r_favorites4 rf
          ON c.course_code = rf.course_code AND rf.student_number =:student_number
          WHERE rf.rating = 'on' 
      """)
      
      result = conn.execute(query, {"student_number": student_number})
      
      favorite_courses = []
      columns = result.keys()
      for row in result:
          result_dict = {column: value for column, value in zip(columns, row)}
          favorite_courses.append(result_dict)
      return favorite_courses


def add_login_to_db(student_number, password, level, education):
  with engine.connect() as conn:
      conn.execute(
          text("INSERT INTO r_users (student_number, password, level, education) VALUES (:student_number, :password, :level, :education)"),
          {"student_number": student_number, "password": password, "level": level, "education": education}
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
    
def add_views_to_db(student_number, course_code, timestamp, id):
  with engine.connect() as conn:
      # Retrieve the 'id' value from the "r_courses" table based on the 'course_code'
      course_info_id = conn.execute(
          text("SELECT id FROM r_courses WHERE course_code = :course_code"),
          {"course_code": course_code}
      ).fetchone()

      if course_info_id:
          course_info_id = course_info_id[0]
      else:
          course_info_id = None

      # Check if a record with the same 'id' and 'student_number' combination already exists in "r_views"
      existing_record = conn.execute(
          text("SELECT id FROM r_views WHERE student_number = :student_number AND id = :id"),
          {"student_number": student_number, "id": course_info_id}
      ).fetchone()

      if not existing_record:
          # If no matching record exists, proceed with the insert
          query = text("INSERT INTO r_views (course_code, student_number, timestamp, id) VALUES (:course_code, :student_number, :timestamp, :id)")
          conn.execute(query, {"course_code": course_code, "student_number": student_number, "timestamp": timestamp, "id": course_info_id})

     



      
     





def get_ratings_from_database(student_number):
  with engine.connect() as conn:
      query = text("SELECT course_code, rating FROM r_favorites4 WHERE student_number = :student_number")
      result = conn.execute(query, {"student_number": student_number})

      # Create a dictionary to store the ratings for each course
      ratings = {row.course_code: row.rating for row in result}
  return ratings

student_number = 'sql@sql.nl'
ratings = get_ratings_from_database(student_number)



def get_recommendations_with_ratings(student_number):
  recommendations = get_recommendations(student_number)  # Retrieve recommended courses as before
  rated_courses = get_ratings_from_database(student_number)  # Retrieve the ratings from the database
  
  for recommendation_set in recommendations:
      for recommendation in recommendation_set['recommended_courses']:
          course_code = recommendation['course_code']  # Access 'course_code' within the nested structure
          # Check if there is a rating for the current course in the rated_courses list
          if course_code in rated_courses:
              recommendation['liked'] = rated_courses[course_code]
              #print(f"Course {course_code} is marked as {rated_courses[course_code]}")
          else:
              # If no rating found, assume 'off'
              recommendation['liked'] = 'off'
              
  
  return recommendations


student_number = 'sql@sql.nl'
recommendations = get_recommendations(student_number)
recommendations = get_recommendations_with_ratings(student_number)











from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from sqlalchemy import create_engine, Column, String
from sqlalchemy import Column, String, Integer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import pandas as pd
import os
from sqlalchemy import create_engine, text

db_connection_string = os.environ['DB_CONNECTION_STRING']

engine = create_engine(
  db_connection_string,
  connect_args={
    "ssl": {
      "ssl_ca": "/etc/ssl/cert.pem"
    }
  }
)



Base = declarative_base()

class Cinfo(Base):
  __tablename__ = 'r_courses'  # Replace with your actual table name

  content = Column(String, primary_key=True)
  course_code = Column(String, primary_key=True)
  course_name = Column(String, primary_key=True)

Session = sessionmaker(bind=engine)
session = Session() 

# Fetch data from the r_views table
course_contents = session.query(Cinfo.content, Cinfo.course_code, Cinfo.course_name).all()

course_contents_df = pd.DataFrame(course_contents, columns=['course_content', 'course_code', 'course_title'])

# Create indices
indices = pd.Series(course_contents_df.index, index=course_contents_df['course_code']).drop_duplicates()

# Now you can access indices using course code


# Close the session
session.close()

Base = declarative_base()

class Cint(Base):
    __tablename__ = 'r_users'  # Replace with your actual table name

    student_number = Column(String, primary_key=True)
    marketing = Column(String)
    economics = Column(String)

Session = sessionmaker(bind=engine)
session = Session()

# Assuming you have your tfidf_matrix and course_content_matrix defined

# Fetch data from the r_users table
course_interests = session.query(Cint.student_number, Cint.marketing, Cint.economics).all()

print(course_interests)


user_interests_list = [
    {'student_number': student_number, 'user_interests': {'marketing': 1 if marketing == 'on' else 0, 'economics': 1 if economics == 'on' else 0}}
    for student_number, marketing, economics in course_interests
]

print(user_interests_list)








course_contents = [row[0] for row in course_contents]
tfidf_vectorizer = TfidfVectorizer()
course_content_matrix = tfidf_vectorizer.fit_transform(course_contents)


from sklearn.metrics.pairwise import cosine_similarity


# Assuming you have your tfidf_matrix and course_content_matrix defined






import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


def get_course_recommendations(student_number):
  user_interest_vector = None

  # Find the user_interest_vector for the specified student_number
  for user_interest in user_interests_list:
    interests = user_interest['user_interests']
    print(interests)

    user_interest_vector = [interests.get(interest, 0) for interest in tfidf_vectorizer.get_feature_names_out()]
    
    
    similarities = cosine_similarity([user_interest_vector], course_content_matrix)

    course_indices = similarities.argsort()[0][::-1]

    print(course_indices)
    

    
    # Recommend the top N courses to the user (e.g., top 5)
    top_n = 5
    recommended_courses = course_contents_df.iloc[course_indices[:top_n]]

    # Display or use the recommended courses
    print(recommended_courses)



student_number = 'sql@sql.nl'
recommendations = get_course_recommendations(student_number)



