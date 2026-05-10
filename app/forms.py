from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

GENRE_CHOICES = [
    ('Action', 'Action'),
    ('Comedy', 'Comedy'),
    ('Drama', 'Drama'),
    ('Horror', 'Horror'),
    ('Thriller', 'Thriller'),
    ('Romance', 'Romance'),
    ('Sci-Fi', 'Sci-Fi'),
    ('Animation', 'Animation'),
    ('Fantasy', 'Fantasy'),
    ('Documentary', 'Documentary'),
    ('Other', 'Other')
]

RATING_CHOICES = [(5, '5 - Excellent'), (4, '4 - Very Good'), (3, '3 - Good'), (2, '2 - Fair'), (1, '1 - Poor')]

IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp', 'svg']


class NameForm(FlaskForm):
    display_name = StringField('Your name', validators=[DataRequired(), Length(min=2, max=80)])
    submit = SubmitField('Enter')


class MovieForm(FlaskForm):
    title = StringField('Movie title', validators=[Optional(), Length(min=2, max=140)])
    tmdb_query = StringField('TMDB search (optional)', validators=[Optional(), Length(max=140)])
    poster_upload = FileField('Upload poster (optional)', validators=[Optional(), FileAllowed(IMAGE_EXTENSIONS, 'Images only!')])
    genre = SelectField('Genre', choices=GENRE_CHOICES, validators=[DataRequired()])
    year = IntegerField('Year', validators=[Optional(), NumberRange(min=1888, max=2100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1200)])
    submit = SubmitField('Save Movie')


class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=RATING_CHOICES, coerce=int, validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[DataRequired(), Length(min=3, max=1000)])
    submit = SubmitField('Post Review')
