"""Database models for SIP311 Project Blog.

This module defines SQLAlchemy models for Users, Posts, Comments, Tags, and PostTag
association for user authentication, blog post management, comment functionality,
and tag organization. The User model includes roles for admin and user privileges.
Posts support markdown content and optional image uploads. Comments are linked to
posts and users, with moderation capabilities. Tags allow categorization of posts.
"""

from datetime import datetime, UTC

from flask_login import UserMixin

from extensions import db

# Association table for Post-Tag many-to-many relationship
post_tag = db.Table(
    'post_tag',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)


class User(db.Model, UserMixin):
    """User model for authentication and role-based access.

    Attributes:
        id: Integer, primary key.
        username: String, unique user identifier, required.
        email: String, unique email address, required.
        password: String, hashed password, required.
        role: String, user role ('admin' or 'user'), default 'user'.
        posts: Relationship, posts authored by the user.
        comments: Relationship, comments authored by the user.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    posts = db.relationship('Post', backref=db.backref('author', lazy=True), lazy=True)
    comments = db.relationship('Comment', backref=db.backref('author', lazy=True), lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def update_role(self, role):
        self.role = role


class Post(db.Model):
    """Blog post model for project updates.

    Attributes:
        id: Integer, primary key.
        title: String, post title, required.
        date: DateTime, publication date, default to current UTC time.
        content: Text, markdown content, required.
        image_path: String, path to optional image in static/images/, nullable.
        user_id: Integer, foreign key to User, required.
        comments: Relationship, comments on the post.
        tags: Relationship, tags associated with the post.
    """
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(200), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True)
    tags = db.relationship('Tag', secondary=post_tag, backref=db.backref('posts', lazy=True))

    def __repr__(self):
        return f'<Post {self.title}>'


class Comment(db.Model):
    """Comment model for user feedback on blog posts.

    Attributes:
        id: Integer, primary key.
        content: Text, comment text, required.
        date: DateTime, comment date, default to current UTC time.
        is_hidden: Boolean, indicates if comment is hidden by admin, default False.
        user_id: Integer, foreign key to User, required.
        post_id: Integer, foreign key to Post, required.
    """
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    is_hidden = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    # New fields for nested comments
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)

    def __repr__(self):
        return f'<Comment {self.id} on Post {self.post_id}>'


class Tag(db.Model):
    """Tag model for categorizing blog posts.

    Attributes:
        id: Integer, primary key.
        name: String, unique tag name, required.
    """
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Tag {self.name}>'
