from __future__ import annotations
from pathlib import Path
from flask import current_app

from pathlib import Path
import os
import re
from typing import Optional

import requests
from flask import current_app
from PIL import Image, ImageDraw, ImageFont
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / 'static'
POSTER_DEFAULT_DIR = STATIC_DIR / 'posters' / 'defaults'
UPLOAD_DIR = STATIC_DIR / 'uploads'

PALETTES = [
    ('#0f172a', '#2563eb', '#38bdf8'),
    ('#3b0764', '#c026d3', '#fb7185'),
    ('#111827', '#f59e0b', '#ef4444'),
    ('#052e16', '#16a34a', '#a3e635'),
    ('#1e1b4b', '#7c3aed', '#f472b6'),
]


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r'[^a-z0-9]+', '_', value)
    value = re.sub(r'_+', '_', value).strip('_')
    return value or 'movie'


def ensure_runtime_dirs() -> None:
    POSTER_DEFAULT_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _wrap_title(title: str, max_len: int = 18) -> list[str]:
    words = title.split()
    lines = []
    current = ''
    for word in words:
        candidate = f'{current} {word}'.strip()
        if len(candidate) <= max_len:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines[:4] or [title[:max_len]]


def _font(size: int, bold: bool = False):
    candidates = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf',
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size=size)
            except Exception:
                pass
    return ImageFont.load_default()


def _title_palette(title: str) -> tuple[str, str, str]:
    idx = sum(ord(c) for c in title) % len(PALETTES)
    return PALETTES[idx]


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def _gradient_image(size: tuple[int, int], palette: tuple[str, str, str]) -> Image.Image:
    width, height = size
    top, mid, bottom = map(_hex_to_rgb, palette)
    img = Image.new('RGB', size)
    px = img.load()
    for y in range(height):
        t = y / max(height - 1, 1)
        if t < 0.55:
            u = t / 0.55
            c1, c2 = top, mid
        else:
            u = (t - 0.55) / 0.45
            c1, c2 = mid, bottom
        rgb = tuple(int(c1[i] + (c2[i] - c1[i]) * u) for i in range(3))
        for x in range(width):
            px[x, y] = rgb
    return img


def _add_overlay(draw: ImageDraw.ImageDraw, size: tuple[int, int]) -> None:
    width, height = size
    shapes = [
        (60, 80, 260, 280, (255, 255, 255, 22)),
        (670, 130, 860, 320, (255, 255, 255, 18)),
        (620, 1040, 890, 1310, (255, 255, 255, 16)),
        (40, 1060, 220, 1240, (255, 255, 255, 13)),
    ]
    for x1, y1, x2, y2, color in shapes:
        draw.ellipse((x1, y1, x2, y2), fill=color)
    draw.rounded_rectangle((85, 890, width - 85, 1170), radius=32, fill=(10, 15, 28, 88))
    for i in range(12):
        x = 110 + i * 63
        draw.rounded_rectangle((x, 1180, x + 28, 1210), radius=8, fill=(255, 255, 255, 30))


def build_jpg_poster(title: str, genre: str, year: int, palette: tuple[str, str, str], tagline: str) -> Image.Image:
    img = _gradient_image((900, 1350), palette).convert('RGBA')
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    _add_overlay(draw, img.size)

    font_brand = _font(34, bold=True)
    font_genre = _font(26, bold=False)
    font_title = _font(72, bold=True)
    font_tagline = _font(32, bold=False)
    font_year = _font(24, bold=False)
    font_bottom = _font(24, bold=True)

    draw.text((450, 82), 'TASMACRITIC', fill=(255, 255, 255, 220), font=font_brand, anchor='ma')
    draw.text((450, 145), genre.upper(), fill=(255, 255, 255, 185), font=font_genre, anchor='ma')

    title_lines = _wrap_title(title)
    line_font = font_title if max(len(line) for line in title_lines) <= 18 else _font(58, bold=True)
    y = 245
    for line in title_lines:
        draw.text((450, y), line, fill=(255, 255, 255, 245), font=line_font, anchor='ma')
        y += 78

    draw.text((450, 1030), tagline, fill=(255, 255, 255, 210), font=font_tagline, anchor='ma')
    draw.text((450, 1095), str(year), fill=(255, 255, 255, 190), font=font_year, anchor='ma')

    pill = (280, 1140, 620, 1208)
    draw.rounded_rectangle(pill, radius=34, fill=(255, 255, 255, 38))
    draw.text((450, 1172), 'Review • Rate • Explore', fill=(255, 255, 255, 240), font=font_bottom, anchor='ma')

    return Image.alpha_composite(img, overlay).convert('RGB')


def save_jpg(image: Image.Image, target_path: Path) -> str:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(target_path, format='JPEG', quality=95, optimize=True)
    return target_path.name


def poster_relative_path(filename: str, subfolder: str = 'posters/defaults') -> str:
    return f'{subfolder}/{filename}'


def default_tagline_for(title: str) -> str:
    return {
        'Interstellar': 'A journey beyond the stars',
        'Kurmanjan Datka': 'A legacy of courage',
        'Fight Club': 'Break the rules',
        'Avatar Aang: The Last Airbender': 'Balance the four nations',
        'F1': 'Speed meets precision',
        'Toy Story': 'Friendship never goes out of style',
        "Heaven Is Beneath Mother's Feet": 'A heartfelt family journey',
        'The Matrix': 'Wake up to reality',
        'The Devil Wears Prada 2': 'Fashion never sleeps',
        'Cars': 'Life in the fast lane',
    }.get(title, 'A movie worth reviewing')


def create_default_poster(title: str, genre: str, year: int, tagline: str) -> str:
    ensure_runtime_dirs()
    filename = f'{slugify(title)}.jpg'
    path = POSTER_DEFAULT_DIR / filename
    palette = _title_palette(title)
    image = build_jpg_poster(title, genre, year, palette, tagline)
    save_jpg(image, path)
    return poster_relative_path(filename)


def save_uploaded_poster(file_storage, movie_slug: str) -> Optional[str]:
    if not file_storage or not getattr(file_storage, 'filename', ''):
        return None

    ensure_runtime_dirs()
    original = secure_filename(file_storage.filename)
    ext = Path(original).suffix.lower() or '.jpg'
    filename = f'{movie_slug}_{os.urandom(4).hex()}{ext}'
    path = UPLOAD_DIR / filename
    file_storage.save(path)
    return f'uploads/{filename}'

def fetch_tmdb_metadata(query: str) -> dict:
    print(current_app.config.get('TMDB_API_KEY'))
    api_key = current_app.config.get('TMDB_API_KEY', '')
    image_base = current_app.config.get('TMDB_IMAGE_BASE', 'https://image.tmdb.org/t/p/w500')
    if not api_key or not query:
        return {}

    search = requests.get(
        'https://api.themoviedb.org/3/search/movie',
        params={'api_key': api_key, 'query': query},
        timeout=15,
    )
    search.raise_for_status()
    results = search.json().get('results', [])
    if not results:
        return {}

    best = results[0]
    metadata = {
        'title': best.get('title') or query,
        'description': best.get('overview') or '',
        'year': int(str(best.get('release_date', '')).split('-')[0]) if best.get('release_date') else None,
        'poster_filename': None,
    }

    poster_path = best.get('poster_path')
    if poster_path:
        poster_url = f"{image_base.rstrip('/')}" + poster_path
        image = requests.get(poster_url, timeout=20)
        image.raise_for_status()
        ext = Path(poster_path).suffix or '.jpg'
        filename = f"{slugify(query)}_{best.get('id', 'tmdb')}{ext}"
        path = UPLOAD_DIR / filename
        path.write_bytes(image.content)
        metadata['poster_filename'] = f'uploads/{filename}'

    return metadata


def delete_poster(relative_path: str) -> None:
    if not relative_path or relative_path.startswith('posters/defaults/'):
        return
    path = STATIC_DIR / relative_path
    if path.exists():
        path.unlink()


def ensure_default_posters():
    defaults = [
        ('Interstellar', 'Sci-Fi', 2014),
        ('Kurmanjan Datka', 'Drama', 2014),
        ('Fight Club', 'Drama', 1999),
        ('Avatar Aang: The Last Airbender', 'Fantasy', 2024),
        ('F1', 'Documentary', 2025),
        ('Toy Story', 'Animation', 1995),
        ("Heaven Is Beneath Mother's Feet", 'Drama', 2023),
        ('The Matrix', 'Sci-Fi', 1999),
        ('The Devil Wears Prada 2', 'Comedy', 2026),
        ('Cars', 'Animation', 2006),
        ('Default', 'Drama', 2024),
    ]
    for title, genre, year in defaults:
        path = POSTER_DEFAULT_DIR / f'{slugify(title)}.jpg'
        if not path.exists():
            create_default_poster(title, genre, year, default_tagline_for(title))

def poster_file_exists(filename):
    poster_path = (
        Path(current_app.root_path)
        / "static"
        / "posters"
        / filename
    )

    return poster_path.exists()