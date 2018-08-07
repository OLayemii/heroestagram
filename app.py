import os
from flask import Flask, render_template, flash, session, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, EqualTo
from config import Config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config.from_object(Config)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
app.config['UPLOAD_FOLDER'] = 'static/img'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), index=True, unique=True)
    password = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.email)


class Hero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    realname = db.Column(db.String(50), index=True, unique=True)
    alterego = db.Column(db.String(50), index=True, unique=True)
    abilities = db.Column(db.String(128))
    quote = db.Column(db.String(128))
    photo_url = db.Column(db.String(128))


db.create_all()


class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[
        DataRequired(),
        EqualTo('confirm', message='Passwords do not match.')
    ])
    confirm = PasswordField("Confirm Password")
    accept_tos = RadioField('', choices=[('yes',
                                          'Do you agree with our <a href="#">terms and conditions</a>')],
                            validators=[DataRequired()])
    submit = SubmitField("Signup")


class AddHero(FlaskForm):
    realname = StringField("Real name", validators=[DataRequired()])
    alterego = StringField("Alter Ego", validators=[DataRequired()])
    abilities = TextAreaField("Abilities")
    quote = TextAreaField("Quote")
    photo = FileField()
    submit = SubmitField("Save")


def checkLogin():
    if session.get('loggedemail'):
        return True
    return False
@app.route("/", methods=['GET', 'POST'])
@app.route("/index", methods=['GET', 'POST'])
def index():
    if checkLogin():
        return redirect(url_for("main"))
    form = LoginForm()
    if form.validate_on_submit():
        email = session['loggedemail'] = form.email.data
        password = form.password.data
        if not User.query.filter_by(email=email, password=password).all():
            flash('Wrong username/password combination')
        else:
            return redirect(url_for('main'))
    else:
        for field in form.errors:
            for error in form.errors[field]:
                flash("{} is required".format(field.title()))

    return render_template('index.html', form=form)


@app.errorhandler(404)
def page_not_found(e):
    return "<h2>Are you lost? </h2>"


@app.route("/logout")
def logout():
    session.pop("loggedemail", None)
    return redirect(url_for("index"))


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if checkLogin():
        return redirect(url_for("main"))
    form = RegisterForm()
    if form.validate_on_submit():
        session['email'] = form.email.data
        session['password'] = form.password.data
        try:
            newuser = User(email=form.email.data, password=form.password.data)
            db.session.add(newuser)
            db.session.commit()

            return redirect(url_for('main'))
        except:
            flash("Error Signing Up")

        return redirect(url_for("signup"))
    else:
        for field in form.errors:
            for error in form.errors[field]:
                if field == 'accept_tos':
                    flash("You have to agree to our terms and conditions.")
                elif field == 'password' and not form.password.data == '':
                    flash(error)
                else:
                    flash("{} is required".format(field.title()))
    return render_template('signup.html', form=form, email=session.get('email'), password=session.get('password'))


@app.route("/main")
def main():
    heroes = Hero.query.order_by(desc(Hero.id))
    return render_template('main.html', heroes=heroes, os=os, __file__=__file__)


@app.route("/addhero", methods=['GET', 'POST'])
def addhero():
    form = AddHero()
    heroes = Hero.query.all()
    return render_template('addhero.html', form=form, heroes=heroes)


@app.route("/uploader", methods=['GET', 'POST'])
def uploader():
    file = request.files['photo']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    realname = request.form.get('realname')
    alterego = request.form.get('alterego')
    abilities = request.form.get('abilities')
    quote = request.form.get('quote')

    hero = Hero(realname=realname, alterego=alterego, abilities=abilities, quote=quote, photo_url=filepath)
    try:
        db.session.add(hero)

        db.session.commit()
        file.save(filepath)
    except:
        flash("Error while adding hero.")


    return redirect(url_for("addhero"))


if __name__ == "__main__":
    app.run(debug=True)