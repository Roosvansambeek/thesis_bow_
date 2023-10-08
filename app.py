from flask import Flask, render_template, jsonify, request, redirect
from database import load_courses_from_db, load_course_from_db, load_best_courses_from_db, load_carousel_courses_from_db, load_explore_courses_from_db, load_compulsory_courses_from_db, add_rating_to_db, get_rating_from_db, remove_rating_from_db

app = Flask(__name__)

filters = {
    'Degree': ['Bachelor', 'Master', 'Pre-master'],
    'Block': [1, 2, 3, 4]
}

@app.route("/")
def landing():
    return render_template('welcome.html')

@app.route("/home")
def home():
    carousel_courses = load_carousel_courses_from_db()
    num_carousel_courses = len(carousel_courses)
    best_courses = load_best_courses_from_db()
    explore_courses = load_explore_courses_from_db()
    compulsory_courses = load_compulsory_courses_from_db()
  
    # Create a dictionary to store ratings for each course
    ratings_dict = {}
    for course in carousel_courses:
        course_code = course['course_code']
        rating_db_carousel = get_rating_from_db(course_code)
        ratings_dict[course_code] = rating_db_carousel

    return render_template('home.html', best_courses=best_courses, carousel_courses=carousel_courses, num_carousel_courses=num_carousel_courses, explore_courses=explore_courses, compulsory_courses=compulsory_courses, ratings_dict=ratings_dict)

@app.route("/courses")
def hello_world():
    courses = load_courses_from_db()
    return render_template('courses.html', courses=courses, filters=filters)

@app.route("/inlogpage")
def load_inlogpage():
    return render_template('inlogpage.html')

@app.route("/welcome")
def welcome():
    return render_template('welcome.html')

@app.route("/api/courses")
def list_courses():
  courses = load_courses_from_db()
  return jsonify(courses)

@app.route("/course/<course_code>")
def show_course(course_code):
  course = load_course_from_db(course_code)
  if not course:
    return "Not Found", 404
  else:
    return render_template('coursepage.html',
                        course=course)

@app.route('/favourites')
def favorite_courses():
    carousel_courses = load_carousel_courses_from_db()
    return render_template('favourites.html', carousel_courses=carousel_courses)

@app.route("/course/<course_code>/rating", methods=['POST'])
def rating_course(course_code):
    data = request.form
    add_rating_to_db(course_code, data)
    previous_page = request.referrer
    return redirect(previous_page)

@app.route("/course/<course_code>/remove_rating", methods=['POST'])
def remove_rating(course_code):
    data = request.form
    remove_rating_from_db(course_code)
    previous_page = request.referrer
    return redirect(previous_page)

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)