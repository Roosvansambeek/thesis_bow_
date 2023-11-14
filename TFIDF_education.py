from sklearn.feature_extraction.text import CountVectorizer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from sqlalchemy import create_engine, Column, String, text, column, String
from sklearn.feature_extraction.text import TfidfVectorizer  
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer 

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

Session = sessionmaker(bind=engine)
session = Session() 

# Fetch data from the r_views table
course_contents = session.query(Cinfo.content, Cinfo.course_code, Cinfo.course_name, Cinfo.degree).all()

course_contents_df = pd.DataFrame(course_contents, columns=['course_content', 'course_code', 'course_title', 'degree'])

# Create indices
indices = pd.Series(course_contents_df.index, index=course_contents_df['course_code']).drop_duplicates()



# Close the session
session.close()

course_contents = [row[0] for row in course_contents]
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
course_content_matrix = tfidf_vectorizer.fit_transform(course_contents)

def recs_on_education_TFIDF(student_number):
  Base = declarative_base()

  class Cedu(Base):
      __tablename__ = 'r_users'  # Replace with your actual table name

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
          # Update the dictionary with terms from the user's education
          for term in education_terms:
              education_dict[term] = 1
          break  
        
          

  

  user_education_vector = [education_dict.get(edu, 0) for edu in tfidf_vectorizer.get_feature_names_out()]
  

  similarities = cosine_similarity([user_education_vector], course_content_matrix)

  course_indices = similarities.argsort()[0][::-1]


   
  top_n = 25
  recommended_courses = course_contents_df.iloc[course_indices[:top_n]]


  student_recommendations = {
      "student_number": student_number,
      "recommended_courses": [
          {
              "course_code": course["course_code"],
              "course_content": course["course_content"],
              "course_title": course["course_title"],
              "degree": course["degree"],
              "similarity_score": similarities[0, index]
          }
          for index, course in recommended_courses.iterrows()
      ]
  }


    # Display or use the recommended courses
  return student_recommendations

    

def get_ratings_from_database(student_number):
  with engine.connect() as conn:
      query = text("SELECT course_code, rating FROM r_favorites4 WHERE student_number = :student_number")
      result = conn.execute(query, {"student_number": student_number})

      # Create a dictionary to store the ratings for each course
      ratings = {row.course_code: row.rating for row in result}
  return ratings


def get_degree_from_database(student_number):
  with engine.connect() as conn:
      query = text("SELECT level FROM r_users WHERE student_number = :student_number")
      result = conn.execute(query, {"student_number": student_number})
  
      levels = [row.level for row in result]
  
  return levels


def get_recommendations_edu_with_ratings_TFIDF(student_number):
  recommendations = recs_on_education_TFIDF(student_number)  # Retrieve recommended courses as before
  rated_courses = get_ratings_from_database(student_number)  # Retrieve the ratings from the database
  #print(rated_courses)

  for recommendation_set in recommendations['recommended_courses']:
    course_code = recommendation_set['course_code']  
    if course_code in rated_courses:
        recommendation_set['rating'] = rated_courses[course_code]
        
    else:
              
      recommendation_set['rating'] = 'off'


  return recommendations


def get_recommendations_edu_level_TFIDF(student_number):
  recommendations = get_recommendations_edu_with_ratings_TFIDF(student_number)
  degree = get_degree_from_database(student_number)


  student_degree = degree[0] if degree else None

  if student_degree:

      filtered_recommendations = {
          "student_number": student_number,
          "recommended_courses": [
              recommendation_set for recommendation_set in recommendations['recommended_courses']
              if recommendation_set['degree'].lower() == student_degree.lower()
          ]
      }
      return filtered_recommendations
  else:
      return {"student_number": student_number, "recommended_courses": []}




