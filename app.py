from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timezone
import os

app = Flask(__name__)

app.config["SECRET_KEY"] = "dev-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    def __repr__(self):
        return f"<Post {self.id} {self.title!r}>"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(120), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationship to Post
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = db.relationship('Post', backref=db.backref('comments', cascade='all, delete-orphan', lazy='dynamic'))

    def __repr__(self):
        return f"<Comment {self.id} on Post {self.post_id!r}>"



@app.route("/")
def home():

    posts = Post.query.order_by(Post.created_at.desc()).all()


    return render_template("index.html", posts=posts)

@app.route("/post/new", methods=["GET", "POST"])
def new_post():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()

        if not title or not body:
            flash("title and body are required")
            return redirect(url_for("new_post"))
        
        post = Post(title=title, body=body)
        db.session.add(post)
        db.session.commit()
        flash("Post Created")
        return redirect(url_for("home"))

    return render_template("new_post.html")

if __name__ == "__main__":
    app.run(debug=True)