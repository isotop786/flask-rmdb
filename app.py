from flask import Flask, request, jsonify
from flask import render_template, flash, redirect, url_for, session, logging
from flaskext.mysql import MySQL
import os
from wtforms import (
    Form,
    StringField,
    TextAreaField,
    PasswordField,
    validators,
    FileField,
)
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename


from data import Articles

# UPLOAD_FOLDER = "static\\img"
UPLOAD_FOLDER = "./web/static"
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}


app = Flask(
    __name__,
    static_url_path="",
    static_folder="web/static",
    template_folder="templates",
)
app.debug = True


# Required
app.config["MYSQL_DATABASE_HOST"] = "localhost"
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = ""
app.config["MYSQL_DATABASE_DB"] = "flaskdb"
app.config["SECRET_KEY"] = "ksdofk2q3423lksdflskdfjsldfklsdf"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# mysql = MySQL(app)
mysql = MySQL()
mysql.init_app(app)

con = mysql.connect()
cursor = con.cursor()


Articles = Articles()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    # return "<h2>Hello, Flask.</h2>"
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/articles")
def articles():
    return render_template("articles.html", articles=Articles)


@app.route("/articles/<string:id>")
def article_details(id):
    return render_template("article.html", id=id)
    # return id


@app.route("/users", methods=["GET", "POST"])
def employee():
    if request.method == "GET":
        # curr = mysql.connection.cursor()
        cursor = mysql.get_db().cursor()
        cursor.execute(""" SELECT * FROM users """)
        results = cursor.fetchall()
    return jsonify(results)


# task form class
class TaskForm(Form):
    title = StringField("Task Name", [validators.Length(min=4, max=100)])
    description = TextAreaField("Description", [validators.Length(min=10, max=1000)])
    # image = FileField("Image File", [validators.regexp("^[^/\\]\.jpg$")])
    image = FileField("Image File")


@app.route("/tasks", methods=["GET", "POST"])
def task():
    form = TaskForm(request.form)
    if request.method == "GET":
        return render_template("create-task.html", form=form)
    if request.method == "POST":
        print(request.files)
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        task_title = form.title.data
        task_des = form.description.data
        task_img = file.filename
        cursor.execute(
            """ INSERT INTO task(title,description,image) VALUES(%s,%s,%s) """,
            (task_title, task_des, task_img),
        )
        con.commit()
        flash("Task added successfully!")
        return redirect("/tasks")


if __name__ == "__main__":
    app.run()
