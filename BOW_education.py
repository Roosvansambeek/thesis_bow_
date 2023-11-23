from sklearn.feature_extraction.text import CountVectorizer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from sqlalchemy import create_engine, Column, String, text, column, String
from sklearn.metrics.pairwise import cosine_similarity
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

# Create indices
indices = pd.Series(course_contents_df.index, index=course_contents_df['course_code']).drop_duplicates()


session.close()

course_contents = [row[0] for row in course_contents]
count_vectorizer = CountVectorizer(stop_words='english')
course_content_matrix = count_vectorizer.fit_transform(course_contents)

def recs_on_education_BOW(student_number):
  Base = declarative_base()

  class Cedu(Base):
      __tablename__ = 'r_users' 

      student_number = Column(String, primary_key=True)
      education = Column(String, primary_key=True)

  Session = sessionmaker(bind=engine)
  session = Session()

 
  # Fetch data from the r_users table
  education_list = session.query(Cedu.student_number, Cedu.education).all()

  session.close()

  user_education_list = [
      {'student_number': student_number, 'education': {'user_education': education.lower()} if education else {'user_education': 'thesis'}}
      for student_number, education in education_list
  ]

  
  
  education_dict = {}

  
  for user in user_education_list:
      if user['student_number'] == student_number:
          education_value = user['education']['user_education']
          education_terms = education_value.lower().split()
          
          for term in education_terms:
              education_dict[term] = 1
          break  
        
          

  

  user_education_vector = [education_dict.get(edu, 0) for edu in count_vectorizer.get_feature_names_out()]
  

  similarities = cosine_similarity([user_education_vector], course_content_matrix)

  course_indices = similarities.argsort()[0][::-1]


   
  top_n = 25
  recommended_courses = course_contents_df.iloc[course_indices[:top_n]]


  student_recommendations = {
      "student_number": student_number,
      "recommended_courses": [
          {
              "course_name": course["course_name"],
              "course_code": course["course_code"],
              "language":course["language"],
              "aims": course["aims"],
              "content": course["content"],
              "degree": course["degree"],
              "ECTS": course['ECTS'],
              "school": course['school'],
              "tests": course['tests'],
              "block": course['block'],
              "lecturers": course['lecturers']
              #"similarity_score": similarities[0, index]
          }
          for index, course in recommended_courses.iterrows()
      ]
  }


    
  return student_recommendations




