# Tasmacritic

**Tasmacritic** is a polished movie review website built for the **Introduction to Web Programming** final project. It combines a clean landing page, a movie catalog, local posters, ratings, reviews, movie management, and optional TMDB poster lookup for user-added movies.

## Problem & Motivation

Tasmacritic presents a full but realistic web application that demonstrates frontend design, backend routing, database storage, form handling, file uploads, pagination, and optional external API integration.

## Features

- **Name-only entry** instead of username/password authentication
- **Hero landing page** with a background image and smooth scroll to the catalog
- **10 default movies** with local posters
- **Add Movie** form with three poster options:
  - use a **TMDB search query (via your TMDB API Key)**,
  - **upload your own poster**,
  - or fall back to a generated local poster
- **Edit movie** and **delete movie** functionality
- **Movie reviews** with 1–5 star ratings
- **Color-coded rating badges**:
  - 5 = green
  - 4 = yellow
  - 3 = orange
  - 2 = light red
  - 1 = strong red
- **Genre dropdown** with the required fixed list
- **Search, filter, and sort** controls
- **Pagination** when the catalog grows beyond 15 films
- **SQLite persistence**

## Default Movies

The app ships with these 10 local movies with their local posters inside the project:

1. Interstellar
2. Kurmanjan Datka
3. Fight Club
4. Avatar Aang: The Last Airbender
5. F1
6. Toy Story
7. Heaven Is Beneath Mother's Feet
8. The Matrix
9. The Devil Wears Prada 2
10. Cars

## Architecture Overview

### Frontend
- HTML templates rendered with Jinja2
- Bootstrap 5 layout
- Custom CSS for the hero, cards, badges, and review styles

### Backend
- Flask application factory
- Blueprints and routes
- Flask-WTF forms
- Optional TMDB poster lookup
- File upload handling for custom posters

### Database
- SQLite database stored in the Flask `instance/` folder
- SQLAlchemy ORM models for movies and reviews

## Tech Stack

- Python 3
- Flask
- Flask-SQLAlchemy
- Flask-WTF
- WTForms
- SQLite
- Requests
- Bootstrap 5
- HTML, CSS, JavaScript

## Project Structure

```text
Movie-Review-Website/
├── app/
│   ├── static/
│   │   ├── css/
│   │   ├── images/
│   │   ├── posters/
│   │   └── uploads/
│   ├── templates/
│   ├── __init__.py
│   ├── forms.py
│   ├── models.py
│   ├── poster_utils.py
│   ├── routes.py
│   └── seed.py
├── docs/
│   ├── ui_flow.svg
├── instance/
├── slides/
│   ├── pitch_deck.pptx
│   ├── pitch_outline.md
├── config.py
├── run.py
├── requirements.txt
├── .env.example
└── README.md
```


## Setup & Run Instructions

### 1. Create a virtual environment

```bash
python -m venv venv
```

### 2. Activate it

**Windows**
```bash
venv\Scripts\activate
```

**macOS / Linux**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Optional: enable TMDB

Copy `.env.example` to `.env` and add your TMDB API key if you want poster lookup for user-added movies.

```env
TMDB_API_KEY=your_tmdb_api_key_here
```

### 5. Run the app

```bash
python run.py
```

### 6. Open the site

```text
http://127.0.0.1:5000
```

## Screenshots / UI Diagram
 
This is a UI flow diagram:

![UI Flow](/docs/ui_flow.svg)

## Pitch Presentation

Slides are included in the repository:

```text
slides/pitch_deck.pptx
slides/pitch_outline.md
```

## Demo Video

* [Demo Video (YouTube)](https://youtu.be/3F6caJzo0Z0)
* [Friend Feedback (YouTube)](https://youtu.be/1ShaZm5mOtE?si=ZBOXFZ6BfKBiaE_n)
