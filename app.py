from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from database import load_courses_from_db, add_rating_to_db, remove_rating_from_db, load_carousel_courses_from_db, load_best_courses_from_db, load_explore_courses_from_db, load_compulsory_courses_from_db, load_favorite_courses_from_db, add_interests_to_db, add_login_to_db, check_credentials, update_interests
from flask import request, redirect, url_for, flash


app = Flask(__name__)


filters = {
    'Degree': ['Bachelor', 'Master', 'Pre-master'],
    'Block': [1, 2, 3, 4]
}

@app.route("/")
def landing():
    return render_template('welcome.html')

app.secret_key = 'session_key'

@app.route("/inlogpage", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student_number = request.form['student_number']
        password = request.form['password']

        if check_credentials(student_number, password):
            session['student_number'] = student_number
            session['password'] = password
            return render_template('state_interests.html')
        else:
            return render_template('inlogpage.html')
    return render_template('inlogpage.html')

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == 'POST':
        student_number = request.form['student_number']
        password = request.form['password']

        if check_credentials(student_number, password):
            return redirect('/inlogpage')
        else:
            add_login_to_db(student_number, password)
            return render_template('state_interests.html')

    return render_template('signin.html')

@app.route("/state_interests.html")
def state_interests():
    return render_template('state_interests.html')

@app.route("/state_interests/stated.html", methods=['POST'])
def stated_interests():
    data = request.form
    student_number = session.get('student_number')  
    password = session.get('password') 

    if student_number and password:
        update_interests(student_number, password, data)

    return redirect('/home')


@app.route("/home")
def home():
    carousel_courses = load_carousel_courses_from_db()
    num_carousel_courses = len(carousel_courses)
    best_courses = load_best_courses_from_db()
    explore_courses = load_explore_courses_from_db()
    compulsory_courses = load_compulsory_courses_from_db()
    return render_template('home.html', best_courses=best_courses, carousel_courses=carousel_courses, num_carousel_courses=num_carousel_courses, explore_courses=explore_courses, compulsory_courses=compulsory_courses)

@app.route("/courses")
def hello_world():
    courses = load_courses_from_db()
    return render_template('courses.html', courses=courses, filters=filters)


@app.route("/welcome")
def welcome():
    return render_template('welcome.html')

@app.route("/api/courses")
def list_courses():
  courses = load_courses_from_db()
  return jsonify(courses)

@app.route("/course/<course_code>")
def show_course(course_code):
  courses = load_courses_from_db()
  course = [course for course in courses if course.get('course_code') == course_code]
  if not course:
    return "Not Found", 404
  else:
    return render_template('coursepage.html',
                        course=course[0])

@app.route('/favourites')
def favorite_courses():
    favorite_courses = load_favorite_courses_from_db()
    return render_template('favourites.html', favorite_courses=favorite_courses)

@app.route("/course/<course_code>/rating", methods=['POST'])
def rating_course(course_code):
    data = request.form
    add_rating_to_db(course_code, data)
    previous_page = request.referrer
    return redirect(previous_page)




@app.route("/course/<course_code>/remove_rating", methods=['POST'])
def remove_rating(course_code):
    data = request.form
    remove_rating_from_db(course_code, data)
    previous_page = request.referrer
    return redirect(previous_page)


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)