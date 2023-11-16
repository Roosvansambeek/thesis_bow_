from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from database import load_courses_from_db, load_carousel_courses_from_db, load_favorite_courses_from_db, add_interests_to_db , add_login_to_db, update_interests, add_views_to_db, add_test_to_db,  load_viewed_courses_from_db, search_courses_from_db, load_ratings_and_details_for_viewed_courses
from flask import request, redirect, url_for, flash
from datetime import datetime



#TFIDF
#fav
from TFIDF_algorithmfav import get_recommendations_fav_with_ratings_TFIDF

#int
from TFIDF_algorithminterests import get_recommendations_level_TFIDF

#edu
from TFIDF_education import get_recommendations_edu_level_TFIDF 

#course
from TFIDF_algorithmcourse import get_recommendations_course_TFIDF

#BOW
#fav
#from BOW_algorithmfav import get_recommendations_fav_BOW, get_recommendations_with_ratings_BOW

#int
#from BOW_algorithminterests import get_course_recommendations_int_BOW, get_recommendations_with_ratings_BOW, get_recommendations_level_BOW

#edu
#from BOW_education import recs_on_education_BOW, get_recommendations_edu_with_ratings_BOW 

#course 
#from BOW_algorithmcourse import get_recommendations_course_BOW


app = Flask(__name__)


@app.route("/")
def landing():
    return render_template('signin.html')

app.secret_key = 'session_key'

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == 'POST':
        student_number = request.form['student_number']
        session['student_number'] = student_number
        level = request.form['level']
        education = request.form['education']

        add_login_to_db(student_number, level, education)

        return redirect('/state_interests.html')

    return render_template('signin.html')

@app.route("/state_interests.html")
def state_interests():
    return render_template('state_interests.html')

@app.route("/state_interests/stated.html", methods=['POST'])
def stated_interests():
    data = request.form
    student_number = session.get('student_number')  
    
  
    if student_number:
        update_interests(student_number, data)

    previous_page = request.referrer
    return redirect(f'/home/{student_number}')



@app.route("/home/<student_number>", methods=['GET', 'POST'])
def home(student_number):
   
    student_number = student_number or session.get('student_number', default_value)
    
    education_recommendations = get_recommendations_edu_level_TFIDF(student_number)
    num_education_recommendations=len(education_recommendations)
    fav_recommendations = get_recommendations_fav_with_ratings_TFIDF(student_number)
    interests_recommendations = get_recommendations_level_TFIDF(student_number)
    viewed_courses=load_ratings_and_details_for_viewed_courses(student_number)

    data = request.form  

    if request.method == 'POST':
        rating = request.form.get('rating')
        course_code = request.form.get('course_code')

        if rating == 'on':
           
            add_test_to_db(request, student_number, course_code, 'on')
        else:
           
            add_test_to_db(request, student_number, course_code, 'off')

       

        fav_recommendations = get_recommendations_fav_with_ratings_TFIDF(student_number)

        interests_recommendations = get_recommendations_level_TFIDF(student_number)

        education_recommendations = get_recommendations_edu_level_TFIDF(student_number)

        viewed_courses=load_ratings_and_details_for_viewed_courses(student_number)



    return render_template('home.html', student_number=student_number, fav_recommendations=fav_recommendations, interests_recommendations=interests_recommendations, viewed_courses=viewed_courses, education_recommendations=education_recommendations)



  
@app.route('/favourites/<student_number>')
def favorite_courses(student_number):
    favorite_courses = load_favorite_courses_from_db(student_number)
    return render_template('favourites.html', favorite_courses=favorite_courses, student_number=student_number)

      
@app.route("/courses/<student_number>")
def hello_world(student_number):
    courses = load_courses_from_db()
    return render_template('courses.html', courses=courses, filters=filters, student_number=student_number)



@app.route("/course/<course_code>/<student_number>")
def show_course(student_number, course_code):
    # Load the course data
    courses = load_courses_from_db()
    viewed_courses=load_viewed_courses_from_db(student_number)
    course_code = request.view_args['course_code']
    recommendations_courses = get_recommendations_course_TFIDF(course_code)
    course = [course for course in courses if course.get('course_code') == course_code]

    if not course:
        return "Not Found", 404

    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    add_views_to_db(student_number, course_code, timestamp, id)

    return render_template('coursepage.html', course=course[0], student_number=student_number, course_code=course_code, recommendations_courses=recommendations_courses)


@app.route("/search", methods=['GET'])
def search():
    query = request.args.get('query')
    student_number = session.get('student_number') # Replace this with the actual 
    results = search_courses_from_db(query)
    return render_template('search_results.html', query=query, results=results, student_number=student_number)

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)