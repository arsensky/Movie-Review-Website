from datetime import datetime

from app import db


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False, index=True)
    genre = db.Column(db.String(40), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    poster_filename = db.Column(db.String(255), nullable=False)
    poster_source = db.Column(db.String(40), nullable=False, default='local')
    added_by = db.Column(db.String(80), nullable=False, default='Tasmacritic')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    reviews = db.relationship('Review', backref='movie', cascade='all, delete-orphan', lazy=True)

    @property
    def review_count(self):
        return len(self.reviews)

    @property
    def average_rating(self):
        if not self.reviews:
            return 0.0
        return round(sum(review.rating for review in self.reviews) / len(self.reviews), 1)

    @property
    def rating_bucket(self):
        avg = self.average_rating
        if avg >= 4.5:
            return 5
        if avg >= 3.5:
            return 4
        if avg >= 2.5:
            return 3
        if avg >= 1.5:
            return 2
        if avg > 0:
            return 1
        return 0


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    author_name = db.Column(db.String(80), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
