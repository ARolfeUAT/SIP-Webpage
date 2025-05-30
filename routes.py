"""Routes for SIP311 Project Blog using a Flask Blueprint.

This module defines a 'main' blueprint containing routes for the homepage, project
blog, SIP brief, boards, projects, contact, user registration, login, logout, and
admin post creation. It integrates with Flask-SQLAlchemy, Flask-Bcrypt, Flask-Login,
Flask-WTF, python-markdown, and SMTP2GO's API.
"""
import os
from datetime import datetime, UTC
import markdown
import requests
from flask import Blueprint, current_app, render_template, request, flash, redirect, url_for, abort
from flask_login import login_user, logout_user, login_required, current_user

from forms import CommentForm, RegisterForm, LoginForm, PostForm

main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Render the homepage.

    Returns:
        str: Rendered HTML template for the homepage.
    """
    return render_template('index.html')


@main.route('/sip')
def sip():
    """Render the project blog page.

    Returns:
        str: Rendered HTML template for the project blog.
    """
    from models import Post

    posts = Post.query.order_by(Post.date.desc()).all()
    form = CommentForm()
    return render_template('sip.html', posts=posts, markdown=markdown, form=form)


@main.route('/sip_brief')
def sip_brief():
    """Render the SIP Brief page.

    Returns:
        str: Rendered HTML template for the SIP Brief.
    """
    return render_template('sip_brief.html')


@main.route('/boards')
def boards():
    """Render the boards page.

    Returns:
        str: Rendered HTML template for the boards page.
    """
    return render_template('boards.html')


@main.route('/projects')
def projects():
    """Render the projects page.

    Returns:
        str: Rendered HTML template for the projects page.
    """
    return render_template('projects.html')


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    """Handle contact form submission and render the contact page.

    Processes form data on POST requests, sending an email via SMTP2GO's API.
    Renders the contact page on GET requests.

    Returns:
        str: Rendered HTML template or redirect on successful submission.
    """
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        payload = {
            'api_key': current_app.config['SMTP2GO_API_KEY'],
            'sender': email,
            'to': ['arolfe90275@uat.edu'],
            'subject': 'SIP Website Contact Form Submitted',
            'text_body': f'Name: {name}\nMessage: {message}'
        }

        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(
                current_app.config['SMTP2GO_API_URL'],
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('main.contact'))
        except requests.RequestException:
            flash('An error occurred while sending your message. Please try again.', 'danger')

    return render_template('contact.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration.

    Creates a new user with 'admin' role for the first user (id=1) and 'user'
    for others. Hashes password and stores user in the database.

    Returns:
        str: Rendered HTML template or redirect on successful registration.
    """
    from extensions import bcrypt, db

    from models import User

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
        )
        db.session.add(user)
        if user.id == 1:
            user.update_role('admin')
        db.session.commit()
        flash('Your account has been created! Please log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login.

    Authenticates user credentials and logs in the user.

    Returns:
        str: Rendered HTML template or redirect on successful login.
    """
    from app import bcrypt
    from models import User

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Login failed. Check email and password.', 'danger')

    return render_template('login.html', form=form)


@main.route('/logout')
@login_required
def logout():
    """Log out the current user.

    Returns:
        str: Redirect to homepage.
    """
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))


@main.route('/sip/add', methods=['GET', 'POST'])
@login_required
def add_post():
    """Handle creation of new blog posts (admin only).

    Allows admin users to create new posts. Non-admin users are denied access.

    Returns:
        str: Rendered HTML template or redirect on successful post creation.
    """
    from app import db
    from models import Post

    if current_user.role != 'admin':
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        # Fetch the form data
        title = request.form.get('title')
        content = request.form.get('content')

        # Convert markdown to html
        html_content = markdown.markdown(content)

        # Prepare your Post model and save to DB
        post = Post(title=title, content=html_content, author=current_user)

        # Check request.files contents
        print(f"request.files: {request.files}")

        # check if the post request has the file part
        if 'image' in request.files:
            image = request.files['image']
            print(f"Image filename: {image.filename}")
            if image.filename != '':
                # save the file and set path to the model post.image_path
                image_path = os.path.join(current_app.root_path, 'static/images', image.filename)
                print(f"Image path: {image_path}")
                image.save(image_path)
                post.image_path = image.filename

        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('main.sip'))

    return render_template('add_post.html', form=form)


# TODO: Remove this route prior to publishing to production
@main.route('/make_me_admin', methods=['GET'])
@login_required
def make_me_admin():
    """
    Assigns the 'admin' role to the currently logged in user and commits
    the change to the database.

    This function is protected by the @login_required decorator, ensuring
    that only logged-in users can promote themselves to admin.

    NOTE: USE ONLY IN DEVELOPMENT MODE.

    Returns:
        str: A message acknowledging the successful change of role.
    """
    from app import db

    current_user.role = 'admin'
    db.session.commit()
    return "You are now an admin!"


@main.route('/post/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_post(id):
    """
    Update a post.

    If the request method is POST, this function will update the post with
    the provided form data and then redirect the user to the post page.
    If the request method is GET, it will render a form for updating post.

    Args:
        id (int): ID of the post to be updated.

    Returns:
        HTTP response.
    """
    from extensions import db
    from models import Post

    # Query our Post by id
    post = Post.query.get_or_404(id)

    # Create an instance of PostForm
    form = PostForm()

    if form.validate_on_submit():
        # Fetch the form data
        post.title = form.title.data
        post.content = form.content.data

        # Save to DB
        db.session.commit()

        flash('Your post has been updated!', 'success')
        return redirect(url_for('main.sip'))

    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    if current_user.role == 'admin':
        return render_template('update_post.html', post=post, form=form)
    else:
        return "401 Unauthorized", 401


@main.route('/post/<int:id>/delete', methods=['GET'])
@login_required
def delete_post(id):
    """
    Delete a post.

    This function will delete the post with the provided ID from the database
    and then redirect the user to the home page.

    Args:
        id (int): ID of the post to be deleted.

    Returns:
        HTTP response.
    """
    from extensions import db
    from models import Post

    if not current_user.role == 'admin':
        return "401 Unauthorized", 401

    # Query our Post by id
    post = Post.query.get_or_404(id)

    # Delete the queried post
    db.session.delete(post)
    db.session.commit()

    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.sip'))


@main.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    from extensions import db
    from models import Comment

    form = CommentForm()
    if form.validate_on_submit():
        # Fetch the form data
        content = form.content.data

        # Prepare your Comment model and save to DB
        comment = Comment(content=content, user_id=current_user.id, post_id=post_id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
        return redirect(url_for('main.sip'))
    else:
        flash('Comment failed. Please try again.', 'danger')
        return redirect(url_for('main.sip'))


@main.route('/test_db')
def test_db():
    """Test database connection."""
    from extensions import db
    from models import User

    try:
        # Try to query the database
        user_count = User.query.count()
        return f"Database connection successful! User count: {user_count}"
    except Exception as e:
        return f"Database connection failed: {str(e)}"
