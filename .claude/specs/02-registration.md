# Spec: Registration

## Overview
This feature turns the existing registration page into a working sign-up flow.
Today `GET /register` only renders the form; the form already POSTs to
`/register`, but there is no handler to process it. This step adds POST
handling so a visitor can create a real account: the submitted name, email,
and password are validated, the password is hashed with werkzeug, and a new
row is inserted into the `users` table (created in Step 1). On success the user
is redirected to the login page; on failure the form re-renders with an error.
Registration is the entry point to every logged-in feature on the Spendly
roadmap (profile, expense tracking), so it must be solid before those steps.

## Depends on
- **Step 1 — Database setup** (`01-database-setup.md`): requires the `users`
  table, `get_db()`, and `init_db()` to already exist. No further dependencies.

## Routes
- `GET /register` — render the empty registration form — **public**
  (already implemented; unchanged behaviour).
- `POST /register` — validate input, create the user, redirect to login on
  success or re-render with an error on failure — **public** (new behaviour
  added to the existing `register` view function).

The existing `register` view will be updated to accept both methods via
`@app.route("/register", methods=["GET", "POST"])`.

## Database changes
No schema changes. The `users` table from Step 1 is sufficient
(`id`, `name`, `email` UNIQUE, `password_hash`, `created_at`).

Two new helper functions are added to `database/db.py` (DB logic must not live
in route functions):
- `get_user_by_email(email)` — returns the matching user row or `None`.
- `create_user(name, email, password_hash)` — inserts a new user and returns
  the new `id`. Both use parameterised queries.

## Templates
- **Create:** none.
- **Modify:** `templates/register.html`
  - Change the hardcoded `action="/register"` to `action="{{ url_for('register') }}"`
    (no hardcoded internal URLs).
  - The existing `{% if error %}` block is reused to display validation errors
    such as "Email already registered" or "Password must be at least 8 characters".
  - Optionally repopulate `name`/`email` values on re-render so the user does
    not lose typed input.

## Files to change
- `app.py` — update the `register` view to handle `GET` and `POST`: read form
  fields, validate, call the db helpers, redirect on success, re-render with
  `error` on failure.
- `database/db.py` — add `get_user_by_email()` and `create_user()` helpers.
- `templates/register.html` — replace hardcoded action with `url_for()` and
  (optionally) preserve submitted values.

## Files to create
- None.

## New dependencies
No new dependencies. `werkzeug.security.generate_password_hash` is already
available (used in Step 1's `seed_db`); `redirect`, `url_for`, and `request`
come from Flask, which is already a dependency.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` via `get_db()` only.
- Parameterised queries only — never use f-strings or string formatting in SQL.
- Passwords hashed with `werkzeug.security.generate_password_hash` — never
  store plaintext; never log the password.
- All DB access goes through helpers in `database/db.py`, not inline in routes.
- Use CSS variables — never hardcode hex values (no template style changes
  expected, but honour this if any are added).
- All templates extend `base.html`.
- Use `url_for()` for every internal link and form action.
- Use `abort()` for HTTP errors; use the form `error` message for user-facing
  validation feedback rather than bare string returns.
- Trim/normalise the email (e.g. `strip().lower()`) before checking uniqueness
  and inserting, so duplicates are caught consistently.

## Definition of done
- [ ] `GET /register` still renders the form with no errors.
- [ ] Submitting valid name + email + password (8+ chars) creates a new row in
      the `users` table with a hashed (non-plaintext) `password_hash`.
- [ ] After a successful registration the browser is redirected to the login
      page (`/login`).
- [ ] Submitting an email that already exists re-renders the form showing an
      "email already registered" error and does **not** create a duplicate row.
- [ ] Submitting a password shorter than 8 characters re-renders the form with
      a validation error and creates no user.
- [ ] Submitting with a missing name, email, or password re-renders with an
      error and creates no user.
- [ ] The registration form's action uses `url_for('register')` (no hardcoded
      URL) and the page extends `base.html`.
- [ ] Verified by inspecting the DB (e.g. `SELECT * FROM users`) that the new
      user exists with a hashed password after a successful sign-up.
