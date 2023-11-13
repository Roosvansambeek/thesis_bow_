from sklearn.feature_extraction.text import CountVectorizer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from sqlalchemy import create_engine, Column, String
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from sqlalchemy import create_engine, text

# Rest of your code...

db_connection_string = os.environ['DB_CONNECTION_STRING']

engine = create_engine(
  db_connection_string,
  connect_args={
    "ssl": {
      "ssl_ca": "/etc/ssl/cert.pem"
    }
  }
)

CountVectorizer = CountVectorizer()

def get_recommendations_course_BOW(course_code):
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
    course_contents = [row[0] for row in course_contents]
    
    course_content_matrix = CountVectorizer.fit_transform(course_contents)
    # Close the session
    session.close()
    
    cosine_sim = cosine_similarity(course_content_matrix, course_content_matrix)
    
    indices = pd.Series(course_contents_df.index, index=course_contents_df['course_code']).drop_duplicates()
    #print(indices)
  

    idx = indices[course_code]
    sim_scores = enumerate(cosine_sim[idx])
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_score = sim_scores[1]

    similar_courses = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    top_recommendations = similar_courses[1:4]
    #print(top_recommendations)

    course_recommendations = {
        "recommended_courses": [
            {
                "course_name": session.query(Cinfo.course_name).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "course_code": session.query(Cinfo.course_code).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "course_content": session.query(Cinfo.content).filter(Cinfo.content == course_contents[course_index]).first()[0],
                "similarity_score": sim_score
            }
            for course_index, similar_courses in top_recommendations
        ]
    }

    top_recommendations.append(course_recommendations)

    #print(top_recommendations)

    return top_recommendations




