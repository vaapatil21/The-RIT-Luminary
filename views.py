from flask import Flask, request, session, redirect, url_for, render_template, flash
from models import User,recent_post,search_by_tags

app = Flask(__name__)


@app.route("/")

@app.route("/")
def index():
    posts = recent_post(5)
    return render_template("index.html", posts=posts)


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User(username)

        if not user.register(password):
            flash("A user with that username already exists.")
        else:
            flash("Successfully signed up.")
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User(username)

        if not user.verify_password(password):
            flash("Invalid login credentials.")
        else:
            flash("Successfully logged in.")
            session["username"] = user.username
            return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/add_post", methods=["POST"])

def add_post():
    title = request.form["title"]
    tags = request.form["tags"]
    text = request.form["text"]

    user = User(session["username"])

    if not title or not tags or not text:
        flash("You must give your post a title, tags, and a text body.")
    else:
        user.add_post(title, tags, text)

    return redirect(url_for("index"))


@app.route("/like_post/<post_id>")
def like_post(post_id):
    username = session.get("username")

    if not username:
        flash("You must be logged in to like a post.")
        return redirect(url_for("login"))

    user = User(username)
    user.like_post(post_id)
    flash("You liked the post.")
    return redirect(request.referrer)

@app.route("/profile/<username>")
def profile(username):
    user1 = User(session.get("username"))
    user2 = User(username)
    posts = user2.recent_posts_user(5)

    similar = []
    common = {}

    if user1.username == user2.username:
        similar = user1.similar_users(3)
    else:
        common = user1.commonality_of_user(user2)

    return render_template("profile.html", username=username, posts=posts, similar=similar, common=common)

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        tags = request.form.get("tags")
        if tags:
            # Split the entered tags and search for posts with matching tags
            tag_list = [tag.strip().lower() for tag in tags.split(",")]
            posts = search_by_tags(tag_list)
        else:
            posts = []

        return render_template("search_results.html", posts=posts)

    return render_template("search.html")


@app.route("/post/<post_id>")
def view_post(post_id):
    # Retrieve and display the post with the given post_id
    # You can implement this logic here
    return render_template("post.html", post=post)



@app.route("/logout")
def logout():
    session.pop("username")
    flash("Successfully Logged out.")
    return redirect(url_for("index"))