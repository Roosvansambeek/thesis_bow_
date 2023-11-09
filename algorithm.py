from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
import os


from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from sqlalchemy import create_engine, Column, String
from sqlalchemy import Column, String, Integer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import numpy as np


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
course_contents = [row[0] for row in course_contents]
# Close the session
session.close()

# Define the SQLAlchemy model for r_views
Base = declarative_base()

class Rfavo(Base):
    __tablename__ = 'r_favorites4'  # Replace with your actual table name

    student_number = Column(String, primary_key=True)
    course_code = Column(String, primary_key=True)
    rating = Column(String)  # Add the rating column to your model
    id = Column(Integer)  # Assuming the 'id' column exists in the table

Session = sessionmaker(bind=engine)
session = Session()

r_favo_data = session.query(Rfavo.student_number, Rfavo.course_code, Rfavo.id).filter(Rfavo.rating == 'on').all()




def get_recommendations(student_number):
  # item-matrix

  tfidf_vectorizer = TfidfVectorizer()
  course_content_matrix = tfidf_vectorizer.fit_transform(course_contents)

  # Create a dictionary to store user profiles
  user_profiles = {}

  # Filter viewed courses for the specified student
  student_views = [(student, course, id) for student, course, id in r_favo_data if student == student_number]

  for student, course, id in student_views:
    if student not in user_profiles:
          user_profiles[student] = {"viewed_courses": []}
    if id is not None:
          user_profiles[student]["viewed_courses"].append(id)

  recommendations = []

  for student, data in user_profiles.items():
      viewed_courses = data["viewed_courses"]
      user_profile = np.asarray(course_content_matrix[viewed_courses].sum(axis=0))
      cosine_similarities = linear_kernel(user_profile, course_content_matrix)
      similar_courses = list(enumerate(cosine_similarities[0]))

      # Sort by similarity and get the top recommendations
      similar_courses = sorted(similar_courses, key=lambda x: x[1], reverse=True)
      top_recommendations = similar_courses[1:6]  # Recommend the top 5 courses

      # Create a dictionary for each student's recommendations
      student_recommendations = {
          "student_number": student,
          "recommended_courses": [
              {
                  "course_name": session.query(Cinfo.course_name).filter(Cinfo.content == course_contents[course_index]).first()[0],
                  "course_code": session.query(Cinfo.course_code).filter(Cinfo.content == course_contents[course_index]).first()[0],
                  "course_content": session.query(Cinfo.content).filter(Cinfo.content == course_contents[course_index]).first()[0],
                  "similarity_score": similarity_score
              }
              for course_index, similarity_score in top_recommendations
          ]
      }

      recommendations.append(student_recommendations)

  return recommendations



session.close()