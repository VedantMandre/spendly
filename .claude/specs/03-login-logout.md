# Spec: Login and Logout

## Overview
This feature makes Spendly's authentication round-trip work end to end. Today
`GET /login` renders a sign-in form, but the form POSTs to `/login` with no
handler to process it, and `/logout` is a placeholder route returning a raw
string. This step adds `POST /login` handling that verifies a user's email and
hashed password and starts a server-side session, and turns `/logout` into a
real route that clears that session. It also introduces Flask session support
(an app `secret_key`) so a logged-in identity persists across requests. Login
and logout are the gate for every authenticated feature on the roadmap
(profile in Step 4, expense tracking in Steps 7–9), so a trustworthy session
flow must exist before any of those steps are built.

## Depends on
- **Step 1 — Database setup** (`01-database-setup.md`): requires the `users`
  table, `get_db()`, and `init_db()`.
- **Step 2 — Registration** (`02-registration.md`): requires `POST /register`
  and the `get_user_by_email()` helper so real accounts exist to log into and
  the same lookup helper can be reused for authentication.

## Routes
- `GET /login` — render the empty sign-in form — **public**
  (already implemented; unchanged behaviour).
- `POST /login` — validate credentials, start a session on success and redirect
  to the landing page (`/`), or re-render the form with an error on failure —
  **public** (new behaviour added to the existing `login` view function).
  While a user is already logged in, both `GET` and `POST /login` redirect to
  the landing page instead of showing the form.
- `GET/POST /register` — while a user is already logged in, redirect to the
  landing page instead of showing the registration form — **public** (guard
  added to the existing `register` view).
- `GET /logout` — clear the session and redirect to the landing page —
  **logged-in** (replaces the current Step 3 placeholder string).

The existing `login` view will be updated to accept both methods via
`@app.route("/login", methods=["GET", "POST"])`, mirroring the `register` view.

## Database changes
No schema changes and no new helper functions. Authentication reuses the
existing `get_user_by_email(email)` helper from Step 2 to fetch the stored
`password_hash`. Password verification uses
`werkzeug.security.check_password_hash` in the route (verification is not a DB
operation, so no new `database/db.py` function is required).

## Templates
- **Create:** none.
- **Modify:**
  - `templates/login.html`
    - Change the hardcoded `action="/login"` to
      `action="{{ url_for('login') }}"` (no hardcoded internal URLs).
    - The existing `{% if error %}` / `auth-error` block is reused to display
      an "Invalid email or password" message on failed sign-in.
    - Optionally repopulate the `email` value on re-render so the user does not
      retype it after a failed attempt.
  - `templates/base.html`
    - The navbar currently always shows "Sign in" and "Get started". Make the
      links session-aware: when `session` holds a logged-in user, show a
      **Logout** link pointing to `{{ url_for('logout') }}` (and optionally a
      Profile link); otherwise show the existing Sign in / Get started links.
      This gives the logout route a reachable entry point in the UI.

## Files to change
- `app.py`
  - Add `secret_key` configuration on the `app` object so sessions can be
    signed (read from an environment variable with a development fallback;
    no new package).
  - Import `session` from Flask and `check_password_hash` from
    `werkzeug.security`.
  - Update the `login` view to handle `GET` and `POST`: read email/password,
    look up the user via `get_user_by_email()`, verify the password hash, set
    `session["user_id"]` (and `session["user_name"]`) on success and redirect
    to the landing route (`/`), or re-render `login.html` with an `error` on
    failure. If a logged-in user hits `login`, redirect them to the landing
    page before processing the form.
  - Add the same already-logged-in guard to the `register` view: redirect a
    logged-in user to the landing page instead of rendering the form.
  - Replace the placeholder `logout` view body with logic that clears the
    session (`session.clear()`) and redirects to `landing`.
- `templates/login.html` — replace the hardcoded action with `url_for()` and
  (optionally) preserve the submitted email.
- `templates/base.html` — make the navbar auth links session-aware.

## Files to create
- None.

## New dependencies
No new dependencies. Flask sessions are built in (`flask.session`), and
`werkzeug.security.check_password_hash` ships with the already-installed
`werkzeug`. No additions to `requirements.txt`.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` via `get_db()` only; reuse
  `get_user_by_email()` rather than writing inline SQL in the route.
- Parameterised queries only — never use f-strings or string formatting in SQL.
- Passwords hashed with werkzeug — verify with `check_password_hash`; never
  compare plaintext, never store or log the raw password.
- Use a generic "Invalid email or password" message for both unknown-email and
  wrong-password cases so the form does not reveal which emails are registered.
- Configure `app.secret_key` from an environment variable with a development
  fallback — do not commit a real secret.
- Use `url_for()` for every internal link and form action — no hardcoded URLs.
- Use `abort()` for HTTP errors; use the form `error` message for user-facing
  validation feedback rather than bare string returns.
- Use CSS variables — never hardcode hex values if any styles are touched.
- All templates extend `base.html`.

## Definition of done
- [ ] `GET /login` still renders the sign-in form with no errors and its form
      action uses `url_for('login')` (no hardcoded URL).
- [ ] Submitting a valid email + correct password redirects to the landing
      page (`/`) and populates the session (`session["user_id"]` is set).
- [ ] A logged-in user visiting `/login` or `/register` is redirected to the
      landing page instead of seeing the form.
- [ ] After logging in, the navbar shows a **Logout** link instead of the
      Sign in / Get started links.
- [ ] Submitting a wrong password re-renders `login.html` with an
      "Invalid email or password" error and does not start a session.
- [ ] Submitting an unregistered email re-renders with the same generic error
      (no indication of whether the email exists) and starts no session.
- [ ] Submitting with a missing email or password re-renders the form with an
      error and starts no session.
- [ ] `GET /logout` clears the session and redirects to the landing page; after
      logout the navbar again shows Sign in / Get started.
- [ ] `app.secret_key` is configured so sessions persist across requests, and
      no real secret value is hardcoded/committed.
- [ ] The demo account (`demo@spendly.com` / `demo123` from `seed_db`) can log
      in successfully, confirming end-to-end auth against a seeded user.
