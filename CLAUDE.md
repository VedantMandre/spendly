# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

This is a teaching/learning project: a personal expense-tracking web app ("Spendly") built with Flask. Many routes and modules are intentionally left as stubs with comments like "Students will implement these" / "Students will write this file in Step N" — the codebase is structured as a step-by-step build-out, so don't be surprised by placeholder routes that just return a string (e.g. `/logout`, `/profile`, `/expenses/add`).

## Commands

Run the dev server (from the project root, with the virtualenv active):
```
python app.py
```
The app runs on `http://localhost:5001` with `debug=True`.

Install dependencies:
```
pip install -r requirements.txt
```

Run tests (pytest + pytest-flask are in requirements.txt, though no test files exist yet):
```
pytest
```

## Architecture

- **`app.py`** — single-file Flask application; all routes are defined here with `@app.route()` and rendered via `render_template()`. There is no blueprint structure — new routes go directly in this file.
- **`database/db.py`** — intended to hold `get_db()` (SQLite connection with `row_factory` and foreign keys enabled), `init_db()` (creates tables with `CREATE TABLE IF NOT EXISTS`), and `seed_db()` (sample data for dev). Currently a stub — not yet implemented.
- **`templates/`** — Jinja2 templates. `base.html` is the shared layout (nav, footer, `{% block title/head/content/scripts %}`); all pages `{% extends "base.html" %}`. Use `url_for()` for all internal links and static assets.
- **`static/css/style.css`** — the single, consolidated stylesheet for the entire site (there is intentionally no per-page CSS file — a previous `landing.css` was merged into this file). It defines the design system as CSS custom properties on `:root`:
  - Colors: `--ink`, `--ink-soft`, `--ink-muted`, `--ink-faint`, `--paper`, `--paper-warm`, `--paper-card`, `--accent` (#1a472a green), `--accent-light`, `--accent-2`, `--danger`, `--border`, `--border-soft`
  - Typography: `--font-display` (DM Serif Display, for headings), `--font-body` (DM Sans, for body text)
  - Layout: `--max-width` (1200px), `--radius-sm/md/lg`
  - When styling new pages/components, reuse these variables rather than hardcoding colors or introducing a new stylesheet.
- **`static/js/main.js`** — shared vanilla JS (currently empty/stub). The project uses **no JS frameworks or libraries** — all interactivity (e.g. the landing page's video modal) is plain vanilla JS, typically as an IIFE in a page's `{% block scripts %}`.

## Conventions observed in the codebase

- Plain-text/legal pages (Terms, Privacy) use a shared `.prose-page` / `.prose-header` / `.prose-title` / `.prose-meta` / `.prose-body` class structure in `style.css` for consistent typography — follow this pattern for any new text-heavy pages rather than writing inline styles.
- The landing page hero and mockup card use an `lp-` prefixed class namespace (`lp-hero`, `lp-badge`, `lp-mockup`, `lp-stat-card`, etc.) kept distinct from other shared classes like `.hero`/`.mock-card`.
- Modal/overlay UI (see the landing page's video modal) follows a vanilla-JS pattern: toggle an `is-open` class plus `aria-hidden`, support closing via close-button click, outside-click (`e.target === overlay`), and Escape key, and — for embedded media — stop playback on close by clearing the `iframe.src` (storing the real URL in a `data-src` attribute).
