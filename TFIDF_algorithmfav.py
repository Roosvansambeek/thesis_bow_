from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, String, Integer
import numpy as np
import pandas as pd



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
  __tablename__ = 'r_courses' 

  content = Column(String, primary_key=True)
  course_code = Column(String, primary_key=True)
  course_name = Column(String, primary_key=True)
  degree= Column(String, primary_key=True)
  language= Column(String, primary_key=True)
  aims= Column(String, primary_key=True)
  content = Column(String, primary_key=True)
  ECTS = Column(String, primary_key=True)
  school = Column(String, primary_key=True)
  tests = Column(String, primary_key=True)
  block = Column(String, primary_key=True)
  lecturers = Column(String, primary_key=True)

Session = sessionmaker(bind=engine)
session = Session() 

# Fetch data from the r_views table
course_contents = session.query(Cinfo.content, Cinfo.course_code, Cinfo.course_name, Cinfo.degree, Cinfo.language, Cinfo.aims, Cinfo.content, Cinfo.ECTS, Cinfo.school, Cinfo.tests, Cinfo.block, Cinfo.lecturers).all()

course_contents_df = pd.DataFrame(course_contents, columns=['course_content', 'course_code', 'course_name', 'degree', 'language', 'aims', 'content', 'ECTS', 'school', 'tests', 'block', 'lecturers'])


course_contents = [row[0] for row in course_contents]

session.close()

# item-matrix

tfidf_vectorizer = TfidfVectorizer(stop_words='english')
course_content_matrix = tfidf_vectorizer.fit_transform(course_contents)


def get_recommendations_fav_TFIDF(student_number):

  Base = declarative_base()
  
  class Rfavo(Base):
      __tablename__ = 'r_sessions'  
  
      student_number = Column(String, primary_key=True)
      course_code = Column(String, primary_key=True)
      activity = Column(String)  
      id_course = Column(Integer)  
  
  Session = sessionmaker(bind=engine)
  session = Session()
  
  r_favo_data = session.query(Rfavo.student_number, Rfavo.course_code, Rfavo.id_course).filter(Rfavo.activity == 'favorited').all()
  

  # Create a dictionary to store user profiles
  user_profiles = {}

  # Filter viewed courses for the specified student
  student_views = [(student, course, id) for student, course, id in r_favo_data if student == student_number]

  for student, course, id_course in student_views:
      if student not in user_profiles:
          user_profiles[student] = {"fav_courses": []}
      if id_course is not None:
          user_profiles[student]["fav_courses"].append(id_course)

  

  recommendations = []


  for student, data in user_profiles.items():
      fav_courses = data["fav_courses"]
      user_profile = np.asarray(course_content_matrix[fav_courses].sum(axis=0))
      cosine_similarities = cosine_similarity(user_profile, course_content_matrix)
      similar_courses = list(enumerate(cosine_similarities[0]))
  
      # Sort by similarity and get the top recommendations
      similar_courses = sorted(similar_courses, key=lambda x: x[1], reverse=True)
      top_recommendations = similar_courses[1:10]  # Recommend the top 5 courses
  
      # Create a dictionary for each student's recommendations
      student_recommendations = {
        "student_number": student,
        "recommended_courses": [
            {
                "course_name": session.query(Cinfo.course_name).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "course_code": session.query(Cinfo.course_code).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "language": session.query(Cinfo.language).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "aims": session.query(Cinfo.aims).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "content": session.query(Cinfo.content).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "degree": session.query(Cinfo.degree).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "ECTS": session.query(Cinfo.ECTS).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "school": session.query(Cinfo.school).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "tests": session.query(Cinfo.tests).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "block": session.query(Cinfo.block).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "lecturers": session.query(Cinfo.lecturers).filter(Cinfo.content == course_contents[course_index]).first()[0],
                #"similarity_score": similarity_score
            }
            for course_index, similarity_score in top_recommendations
        
        ]
      }
  
      recommendations.append(student_recommendations)

      session.close()

  return recommendations
  



