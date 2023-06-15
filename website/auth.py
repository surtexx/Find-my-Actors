from . import db
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from .models import Actor
from .models import Submission
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask import current_app
from FMA import FMA
from io import BytesIO
from werkzeug.utils import secure_filename
import os
from werkzeug.datastructures import FileStorage
from PIL import Image

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect (url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')

        if len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(last_name) < 2:
            flash('Last name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            # add user to database
            new_user = User(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
    return render_template("sign_up.html", user=current_user)


# Actor CRUD routes

@auth.route('/actors/<int:actor_id>')
def actor(actor_id):
    actor = Actor.query.get(actor_id)
    uploads = Submission.query.filter_by(actorid=actor_id).all()
    return render_template("actor.html", actor=actor, user=current_user, uploads=uploads, os=os)

UPLOAD_FOLDER = 'static/images'

@auth.route('/actors')
def all_actors():
    actors = Actor.query.all()
    return render_template('all_actors.html', user=current_user, actors=actors, os=os)

@auth.route('/actors/new', methods=['GET', 'POST'])
@login_required
def new_actor():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        image = request.files.get('image')

        actor = Actor.query.filter_by(name=name).first()
        if actor:
            flash('Actor already exists.', category='error')
        else:
            # save image to static folder
            filename = secure_filename(image.filename)
            image_path = os.path.join(current_app.root_path, 'static/images', filename)
            image.save(image_path)

            # add actor to database
            new_actor = Actor(name=name, description=description, image=filename)
            db.session.add(new_actor)
            db.session.commit()

            flash('Actor created!', category='success')
            return redirect(url_for('auth.actor', actor_id=new_actor.id))

    return render_template("new_actor.html", user=current_user, os=os)

@auth.route('/actors/<int:actor_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_actor(actor_id):
    actor = Actor.query.get(actor_id)
    if request.method == 'POST':
        actor.name = request.form.get('name')
        actor.description = request.form.get('description')

        # Check if a new image file was uploaded
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                # Save image to the static folder
                filename = secure_filename(image.filename)
                image_path = os.path.join(current_app.root_path, 'static/images', filename)
                image.save(image_path)
                actor.image = filename

        db.session.commit()
        flash('Actor updated!', category='success')
        return redirect(url_for('auth.actor', actor_id=actor.id))

    return render_template("edit_actor.html", actor=actor, user=current_user)

@auth.route('/actors/<int:actor_id>/delete', methods=['POST'])
@login_required
def delete_actor(actor_id):
    actor = Actor.query.get(actor_id)
    db.session.delete(actor)
    db.session.commit()
    flash('Actor deleted!', category='success')
    return redirect(url_for('auth.all_actors', user=current_user))


@auth.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    image_file = request.files.get('image')
    filename = secure_filename(image_file.filename)
    image_path = os.path.join(current_app.root_path, 'static', 'images', filename)
    image_file.save(image_path)

    model_ai = FMA()
    prediction_image, actors_found = model_ai.predict(image_path)
    prediction_image = Image.fromarray(prediction_image)
    actors_found = model_ai.predict(image_path)[1]
    prediction_image_filename = filename.split(".")[0] + "_prediction." + filename.split(".")[1]
    prediction_image_path = os.path.join(current_app.root_path, 'static', 'images',
                                                      prediction_image_filename)
    image_buffer = BytesIO()
    prediction_image.save(image_buffer, format="JPEG")
    image_buffer.seek(0)
    prediction_image_content = image_buffer.read()

    image_file_prediction = FileStorage(stream=BytesIO(prediction_image_content), filename=prediction_image_filename)
    image_file_prediction.save(prediction_image_path)

    if len(actors_found) == 0:
        flash('Actor not found!', category='error')
    else:

        for actor_found in set(actors_found):
            all_actors = Actor.query.all()
            for actor in all_actors:

                new_actor = actor.name.lower()

                if new_actor == actor_found.lower():
                    id_actor = Actor.query.filter_by(name=actor.name).first().id
                    new_submission = Submission(image=filename, actorid=id_actor)
                    db.session.add(new_submission)
                    db.session.commit()
                    subm = Submission.query.filter_by(image=filename).first()
                    flash('Actor found!', category='success')

        return render_template("home.html", user=current_user, image_file=image_file_prediction, prediction= actors_found)

    return render_template("home.html", user=current_user, image_file=image_file, prediction= None)