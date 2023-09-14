from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, URLField, IntegerField
from wtforms.validators import DataRequired, Length, URL

app = Flask(__name__)
app.config['SECRET_KEY'] = ''
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer(), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float(2), nullable=False)
    ranking = db.Column(db.Integer(), nullable=False)
    image = db.Column(db.String(600), nullable=False)

    def __repr__(self):
        # return '<title %r>' % self.title
        return f'{self.title}({self.year})-{self.rating}/10'


class EditMovie(FlaskForm):
    rating = FloatField(label='Rating', validators=[DataRequired(message="New Rating Required!")])
    ranking = IntegerField(label='Ranking', validators=[DataRequired(message="Ranking Required!")])
    submit = SubmitField('Submit')


class AddMovie(FlaskForm):
    title = StringField(label='Movie Title', validators=[DataRequired(message="Title Required!"),
                                                         Length(min=1, max=150, message="Name limit reached!")])
    year = IntegerField(label='Year', validators=[DataRequired(message="Year Required!"),
                                                  Length(min=4, max=4, message="Invalid Year!")])
    description = StringField(label='Description', validators=[DataRequired(message="Description Required!")])
    rating = FloatField(label='Rating', validators=[DataRequired(message="Rating Required!")])
    ranking = IntegerField(label='Ranking', validators=[DataRequired(message="Rank Required!")])
    image = URLField(label='Poster: ', validators=[DataRequired(message="Image Required!"), URL(message="Invalid")])
    submit = SubmitField('Submit')


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    movies = Movie.query.order_by("ranking")

    return render_template("index.html", movies=movies)


@app.route("/edit?id=<id>", methods=['GET', 'POST'])
def edit(id):
    form = EditMovie(meta={'csrf': False})
    movie_edit = Movie.query.filter_by(id=id).first()
    if request.method == "POST":
        movie_edit.rating = request.form['rating']
        movie_edit.ranking = request.form['ranking']
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", movie=movie_edit, form=form)


@app.route("/delete?id=<id>")
def delete(id):
    Movie.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=['GET', 'POST'])
def add():
    form = AddMovie(meta={'csrf': False})
    if request.method == "POST":
        new_movie = Movie(title=request.form['title'], year=request.form['year'],
                          description=request.form['description'], rating=request.form['rating'],
                          ranking=request.form['ranking'], image=request.form['image'])
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add.html", form=form)


if __name__ == '__main__':
    app.run(debug=True)
