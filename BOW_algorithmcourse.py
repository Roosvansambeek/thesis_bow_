from sklearn.feature_extraction.text import CountVectorizer
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

count_vectorizer = CountVectorizer(stop_words='english')

def get_recommendations_course_BOW(course_code):
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

    
    indices = pd.Series(course_contents_df.index, index=course_contents_df['course_code']).drop_duplicates()
    
    
    course_contents = [row[0] for row in course_contents]
    
    course_content_matrix = count_vectorizer.fit_transform(course_contents)
    
    session.close()
    
    cosine_sim = cosine_similarity(course_content_matrix, course_content_matrix)
    
    indices = pd.Series(course_contents_df.index, index=course_contents_df['course_code']).drop_duplicates()
    


    idx = indices[course_code]
    sim_scores = enumerate(cosine_sim[idx])
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_score = sim_scores[1]

    similar_courses = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    top_recommendations = similar_courses[1:4]
    

    course_recommendations = {
        "recommended_courses": [
            {
                "course_name": session.query(Cinfo.course_name).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "course_code": session.query(Cinfo.course_code).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "content": session.query(Cinfo.content).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "degree": session.query(Cinfo.degree).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "language": session.query(Cinfo.language).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "aims": session.query(Cinfo.aims).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "ECTS": session.query(Cinfo.ECTS).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "school": session.query(Cinfo.school).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "tests": session.query(Cinfo.tests).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "block": session.query(Cinfo.block).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "lecturers": session.query(Cinfo.lecturers).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "similarity_score": sim_score
            }
            for course_index, similar_courses in top_recommendations
        ]
    }

    top_recommendations.append(course_recommendations)
  
    #print(top_recommendations)

    return top_recommendations




