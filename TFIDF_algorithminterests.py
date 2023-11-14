


from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from sqlalchemy import create_engine, Column, String
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
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

# Now you can access indices using course code
course_contents = [row[0] for row in course_contents]
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
course_content_matrix = tfidf_vectorizer.fit_transform(course_contents)

# Close the session
session.close()

def get_course_recommendations_int_TFIDF(student_number):

  Base = declarative_base()
  
  class Cint(Base):
      __tablename__ = 'r_users'  # Replace with your actual table name
  
      student_number = Column(String, primary_key=True)
      management = Column(String)
      data = Column(String)
      law = Column(String)
      businesses = Column(String)
      psychology = Column(String)
      economics = Column(String)
      statistics = Column(String)
      finance = Column(String)
      philosophy = Column(String)
      sociology = Column(String)
      entrepreneurship = Column(String)
      marketing = Column(String)
      accounting = Column(String)
      econometrics = Column(String)
      media = Column(String)
      ethics = Column(String)
      programming = Column(String)
      health = Column(String)
      society = Column(String)
      technology = Column(String)
      communication = Column(String)
      history = Column(String)
      culture = Column(String)
      language = Column(String)
  
  Session = sessionmaker(bind=engine)
  session = Session()
  
  # Assuming you have your tfidf_matrix and course_content_matrix defined
  
  # Fetch data from the r_users table
  course_interests = session.query(Cint.student_number, Cint.management, Cint.data, Cint.law, Cint.businesses, Cint.psychology, Cint.economics, Cint.statistics, Cint.finance, Cint.philosophy, Cint.sociology, Cint.entrepreneurship, Cint.marketing, Cint.accounting, Cint.econometrics, Cint.media, Cint.ethics, Cint.programming, Cint.health, Cint.society, Cint.technology, Cint.communication, Cint.history, Cint.culture, Cint.language).all()
  
  session.close()
  
  user_interests_list = [
      {'student_number': student_number, 'user_interests': {'management': 1 if management == 'on' else 0, 'data': 1 if data == 'on' else 0, 'law': 1 if law == 'on' else 0, 'businesses': 1 if businesses == 'on' else 0, 'psychology': 1 if psychology == 'on' else 0, 'economics': 1 if economics == 'on' else 0, 'statistics': 1 if statistics == 'on' else 0, 'finance': 1 if finance == 'on' else 0, 'philosophy': 1 if philosophy == 'on' else 0, 'sociology': 1 if sociology == 'on' else 0, 'entrepreneurship': 1 if entrepreneurship == 'on' else 0, 'marketing': 1 if marketing == 'on' else 0, 'accounting': 1 if accounting == 'on' else 0, 'econometrics': 1 if econometrics == 'on' else 0, 'media': 1 if media == 'on' else 0, 'ethics': 1 if ethics == 'on' else 0, 'programming': 1 if programming == 'on' else 0, 'health': 1 if health == 'on' else 0, 'society': 1 if society == 'on' else 0, 'technology': 1 if technology == 'on' else 0, 'communication': 1 if communication == 'on' else 0, 'history': 1 if history == 'on' else 0, 'culture': 1 if culture == 'on' else 0, 'language': 1 if language == 'on' else 0}}
      for student_number, management, data, law, businesses, psychology, economics, statistics, finance, philosophy, sociology, entrepreneurship, marketing, accounting, econometrics, media, ethics, programming, health, society, technology, communication, history, culture, language in course_interests
  ]
  
  
  


  user_interest_vector = None

  # Find the user_interest_vector for the specified student_number
  for user_interest in user_interests_list:
    interests = user_interest['user_interests']

    
    user_interest_vector = [interests.get(interest, 0) for interest in tfidf_vectorizer.get_feature_names_out()]


    similarities = cosine_similarity([user_interest_vector], course_content_matrix)

    course_indices = similarities.argsort()[0][::-1]


    top_n = 50
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

      # Create a list to store the levels for the student
      levels = [row.level for row in result]

  return levels



def get_recommendations_with_ratings_TFIDF(student_number):
  recommendations = get_course_recommendations_int_TFIDF(student_number) 
  rated_courses = get_ratings_from_database(student_number) 

  for recommendation_set in recommendations['recommended_courses']:
      course_code = recommendation_set['course_code']
      if course_code in rated_courses:
          recommendation_set['rating'] = rated_courses[course_code]
          print(f"Course {course_code} is marked as {rated_courses[course_code]}")
      else:
          recommendation_set['rating'] = 'off'

  return recommendations



def get_recommendations_level_TFIDF(student_number):
  recommendations = get_recommendations_with_ratings_TFIDF(student_number)
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





