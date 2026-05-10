from __future__ import annotations

from datetime import datetime
from pathlib import Path
import math
import re

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from sqlalchemy import desc, asc

from . import db
from .forms import GENRE_CHOICES, MovieForm, NameForm, ReviewForm
from .models import Movie, Review
from .poster_utils import (
    delete_poster,
    fetch_tmdb_metadata,
    poster_file_exists,
    save_uploaded_poster,
    slugify,
)

bp = Blueprint('main', __name__)
PER_PAGE = 15
SORT_OPTIONS = [
    ('rating_desc', 'Highest rating'),
    ('rating_asc', 'Lowest rating'),
    ('year_desc', 'Newest first'),
    ('year_asc', 'Oldest first'),
    ('title_asc', 'Title A-Z'),
]


def current_name() -> str:
    return session.get('display_name', 'Guest')


@bp.context_processor
def inject_globals():
    return {
        'current_name': current_name(),
        'all_movie_count': Movie.query.count(),
        'genre_choices': GENRE_CHOICES,
        'sort_options': SORT_OPTIONS,
    }


def _movie_rating_key(movie: Movie) -> tuple:
    avg = movie.average_rating
    if avg == 0:
        avg = -1
    return avg


def _sort_movies(items: list[Movie], sort_mode: str) -> list[Movie]:
    if sort_mode == 'rating_asc':
        return sorted(items, key=lambda m: (m.average_rating, m.title.lower()))
    if sort_mode == 'year_desc':
        return sorted(items, key=lambda m: (-m.year, m.title.lower()))
    if sort_mode == 'year_asc':
        return sorted(items, key=lambda m: (m.year, m.title.lower()))
    if sort_mode == 'title_asc':
        return sorted(items, key=lambda m: m.title.lower())
    return sorted(items, key=lambda m: (-m.average_rating, m.title.lower()))


def _filtered_movies(query: str = '', genre: str = '', sort_mode: str = 'rating_desc') -> list[Movie]:
    movies = Movie.query.all()
    q = query.strip().lower()
    filtered = []
    for movie in movies:
        if q and q not in movie.title.lower() and q not in movie.description.lower() and q not in movie.genre.lower():
            continue
        if genre and movie.genre != genre:
            continue
        filtered.append(movie)
    return _sort_movies(filtered, sort_mode)


def _movie_pagination(items: list[Movie], page: int):
    total = len(items)
    total_pages = max(math.ceil(total / PER_PAGE), 1)
    page = max(1, min(page, total_pages))
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    page_items = items[start:end]
    return page_items, total, total_pages, start, min(end, total)


def _save_movie_poster(form: MovieForm, movie: Movie) -> None:
    tmdb_query = (form.tmdb_query.data or '').strip()
    uploaded = form.poster_upload.data
    poster_filename = None
    poster_source = 'local'

    if tmdb_query:
        try:
            metadata = fetch_tmdb_metadata(tmdb_query)
        except Exception as exc:  # noqa: BLE001
            flash(f'TMDB lookup failed: {exc}', 'warning')
            metadata = {}

        if metadata.get('poster_filename'):
            poster_filename = metadata['poster_filename']
            poster_source = 'tmdb'
        if not movie.description and metadata.get('description'):
            movie.description = metadata['description']
        if not movie.year and metadata.get('year'):
            movie.year = metadata['year']

    if uploaded and getattr(uploaded, 'filename', ''):
        poster_filename = save_uploaded_poster(uploaded, slugify(movie.title))
        poster_source = 'upload'

    if not poster_filename:
        poster_filename = None

    movie.poster_filename = poster_filename or movie.poster_filename or 'posters/defaults/default.jpg'
    movie.poster_source = poster_source if poster_filename else movie.poster_source


@bp.route('/', methods=['GET', 'POST'])
def index():
    name_form = NameForm()
    if name_form.validate_on_submit():
        session['display_name'] = name_form.display_name.data.strip()
        flash(f'Welcome, {session["display_name"]}!', 'success')
        return redirect(url_for('main.index'))

    q = request.args.get('q', '')
    genre = request.args.get('genre', '')
    sort_mode = request.args.get('sort', 'rating_desc')
    page = request.args.get('page', 1, type=int)

    movies = _filtered_movies(q, genre, sort_mode)
    page_movies, total_movies, total_pages, start, end = _movie_pagination(movies, page)

    return render_template(
        'index.html',
        name_form=name_form,
        movies=page_movies,
        query=q,
        selected_genre=genre,
        sort_mode=sort_mode,
        total_movies=total_movies,
        total_pages=total_pages,
        page=page,
        showing_start=(start + 1) if total_movies else 0,
        showing_end=end,
    )


@bp.route('/movies')
def movies_page():
    return redirect(url_for('main.index', **request.args))


@bp.route('/movie/<int:movie_id>', methods=['GET', 'POST'])
def movie_detail(movie_id: int):
    movie = Movie.query.get_or_404(movie_id)
    form = ReviewForm()

    if form.validate_on_submit():
        review = Review(
            movie_id=movie.id,
            author_name=current_name(),
            rating=form.rating.data,
            comment=form.comment.data.strip(),
        )
        db.session.add(review)
        db.session.commit()
        flash('Review posted successfully.', 'success')
        return redirect(url_for('main.movie_detail', movie_id=movie.id))

    return render_template('movie_detail.html', movie=movie, form=form)


@bp.route('/movies/add', methods=['GET', 'POST'])
def add_movie():
    form = MovieForm()
    if form.validate_on_submit():
        title = form.title.data.strip()
        movie = Movie(
            title=title,
            genre=form.genre.data,
            year=form.year.data or datetime.utcnow().year,
            description=(form.description.data or '').strip(),
            poster_filename='posters/defaults/default.jpg',
            poster_source='local',
            added_by=current_name(),
        )

        _save_movie_poster(form, movie)

        # If the TMDB query is used, let it fill missing text fields.
        if not movie.description and form.tmdb_query.data:
            try:
                metadata = fetch_tmdb_metadata(form.tmdb_query.data.strip())
            except Exception:
                metadata = {}
            if metadata.get('description'):
                movie.description = metadata['description']
            if metadata.get('year'):
                movie.year = metadata['year']

        if not movie.description:
            flash('Add a description or us'
                  'e TMDB lookup to auto-fill it.', 'danger')
            return render_template('movie_form.html', form=form, mode='add')

        if not movie.year:
            flash('Year is required unless TMDB provides it.', 'danger')
            return render_template('movie_form.html', form=form, mode='add')

        db.session.add(movie)
        db.session.commit()
        flash(f'{movie.title} added successfully.', 'success')
        return redirect(url_for('main.movie_detail', movie_id=movie.id))

    return render_template('movie_form.html', form=form, mode='add')


@bp.route('/movies/<int:movie_id>/edit', methods=['GET', 'POST'])
def edit_movie(movie_id: int):
    movie = Movie.query.get_or_404(movie_id)
    form = MovieForm(obj=movie)
    if request.method == 'GET':
        form.year.data = movie.year

    if form.validate_on_submit():
        movie.title = form.title.data.strip()
        movie.genre = form.genre.data
        movie.year = form.year.data or movie.year
        movie.description = (form.description.data or '').strip() or movie.description

        old_poster = movie.poster_filename
        tmdb_query = (form.tmdb_query.data or '').strip()

        if tmdb_query or (form.poster_upload.data and getattr(form.poster_upload.data, 'filename', '')):
            _save_movie_poster(form, movie)
            if old_poster != movie.poster_filename:
                delete_poster(old_poster)

        db.session.commit()
        flash(f'{movie.title} updated successfully.', 'success')
        return redirect(url_for('main.movie_detail', movie_id=movie.id))

    return render_template('movie_form.html', form=form, mode='edit', movie=movie)


@bp.route('/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(movie_id: int):
    movie = Movie.query.get_or_404(movie_id)
    poster = movie.poster_filename
    db.session.delete(movie)
    db.session.commit()
    delete_poster(poster)
    flash('Movie deleted.', 'info')
    return redirect(url_for('main.index'))


@bp.route('/reviews/<int:review_id>/delete', methods=['POST'])
def delete_review(review_id: int):
    review = Review.query.get_or_404(review_id)
    movie_id = review.movie_id
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted.', 'info')
    return redirect(url_for('main.movie_detail', movie_id=movie_id))
