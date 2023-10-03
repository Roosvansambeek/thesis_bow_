from flask import Flask, render_template, jsonify
from database import load_courses_from_db, load_course_from_db

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
    return render_template('home.html')

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
    return render_template('favourites.html')


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)