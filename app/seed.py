from app import db
from app.models import Movie, Review
from app.poster_utils import create_default_poster, ensure_default_posters, slugify, default_tagline_for

DEFAULT_MOVIES = [
    {
        'title': 'Interstellar',
        'genre': 'Sci-Fi',
        'year': 2014,
        'description': 'A team of explorers travels through a wormhole in space in an attempt to ensure humanity’s survival.',
    },
    {
        'title': 'Kurmanjan Datka',
        'genre': 'Drama',
        'year': 2014,
        'description': 'A historical drama about the legendary Kyrgyz queen and her role in national history.',
    },
    {
        'title': 'Fight Club',
        'genre': 'Drama',
        'year': 1999,
        'description': 'An insomniac office worker and a soap maker form an underground fight club with strict rules.',
    },
    {
        'title': 'Avatar Aang: The Last Airbender',
        'genre': 'Fantasy',
        'year': 2024,
        'description': 'A young Avatar must master all four elements to restore balance to a divided world.',
    },
    {
        'title': 'F1',
        'genre': 'Documentary',
        'year': 2025,
        'description': 'A fast-paced story about the world of Formula 1 racing, strategy, and the pursuit of victory.',
    },
    {
        'title': 'Toy Story',
        'genre': 'Animation',
        'year': 1995,
        'description': 'A cowboy doll feels threatened when a new spaceman figure joins the toy box.',
    },
    {
        'title': "Heaven Is Beneath Mother's Feet",
        'genre': 'Drama',
        'year': 2023,
        'description': 'A touching story about family, sacrifice, and the bond between a mother and child.',
    },
    {
        'title': 'The Matrix',
        'genre': 'Sci-Fi',
        'year': 1999,
        'description': 'A hacker discovers the unsettling truth about the reality he lives in.',
    },
    {
        'title': 'The Devil Wears Prada 2',
        'genre': 'Comedy',
        'year': 2026,
        'description': 'The stylish sequel explores ambition, fashion, and the chaotic world behind the runway.',
    },
    {
        'title': 'Cars',
        'genre': 'Animation',
        'year': 2006,
        'description': 'A racing car learns that winning is not the only thing that matters in life.',
    },
]

SEED_REVIEWS = [
    ('Interstellar', 'Arsen', 5, 'A masterpiece with a powerful emotional core.'),
    ('Kurmanjan Datka', 'Ainura', 5, 'Important and inspiring history lesson.'),
    ('Fight Club', 'Bek', 4, 'Dark, sharp, and unforgettable.'),
    ('Avatar Aang: The Last Airbender', 'Dana', 4, 'Beautiful world and strong visual design.'),
    ('F1', 'Maksat', 3, 'Informative and energetic.'),
    ('Toy Story', 'Nuria', 5, 'Still heartwarming after all these years.'),
    ("Heaven Is Beneath Mother's Feet", 'Aidar', 5, 'Very emotional and meaningful.'),
    ('The Matrix', 'Sultan', 5, 'A classic that still feels modern.'),
    ('The Devil Wears Prada 2', 'Mira', 2, 'Fun idea, but the sequel is only imagined right now.'),
    ('Cars', 'Alina', 4, 'A charming and colorful film.'),
]


def seed_default_data():
    ensure_default_posters()
    if Movie.query.count() > 0:
        return

    movies = []
    for item in DEFAULT_MOVIES:
        slug = slugify(item['title'])
        poster_filename = f'posters/defaults/{slug}.jpg'
        if not (poster_filename and (create_default_poster(item['title'], item['genre'], item['year'], default_tagline_for(item['title'])) or True)):
            poster_filename = f'posters/defaults/{slug}.jpg'
        movie = Movie(
            title=item['title'],
            genre=item['genre'],
            year=item['year'],
            description=item['description'],
            poster_filename=poster_filename,
            poster_source='local',
            added_by='Tasmacritic',
        )
        db.session.add(movie)
        movies.append(movie)

    db.session.flush()

    for movie_title, author, rating, comment in SEED_REVIEWS:
        movie = next((m for m in movies if m.title == movie_title), None)
        if movie:
            db.session.add(Review(movie_id=movie.id, author_name=author, rating=rating, comment=comment))

    db.session.commit()
