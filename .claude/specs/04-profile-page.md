# Spec: Profile Page Design

## Overview
This feature replaces the `/profile` placeholder with a real, logged-in account
dashboard. Previously `GET /profile` returned a raw string ("Profile page —
coming in Step 4"), even though the navbar already links to it for authenticated
users (added in Step 3). This step implements a protected profile view that
fetches the signed-in user's record and renders a designed dashboard showing:
their account details (display name, email, member-since date); a summary stat
row (total spent in ₹, transaction count, top spending category); a **recent
transactions** list; and an **expenses-by-category** breakdown with proportional
bars — all read-only, drawn from the already-seeded `expenses` table. On a
successful login the user is now sent straight to this page. It is the first
authenticated, data-backed page on the Spendly roadmap and establishes the
pattern (login guard → DB helpers → template reusing the existing design system)
that the expense screens in Steps 7–9 will reuse.

## Depends on
- **Step 1 — Database setup** (`01-database-setup.md`): the `users` and
  `expenses` tables, `get_db()`, and `init_db()`.
- **Step 2 — Registration** (`02-registration.md`): real accounts must exist so
  a profile has data to display.
- **Step 3 — Login and Logout** (`03-login-logout.md`): the session keys
  (`session["user_id"]`, `session["user_name"]`) that identify which user's
  profile to show, and the navbar Profile link that reaches this page.

## Routes
- `GET /profile` — render the signed-in user's profile dashboard; if no user is
  logged in, redirect to `GET /login` — **logged-in** (replaces the Step 4
  placeholder string in the existing `profile` view). Also handles a stale
  session (a `user_id` whose row no longer exists) by clearing the session and
  redirecting to login.
- `POST /login` (existing, Step 3) — modified: on a **successful** login the
  redirect target changes from `landing` to `profile` (`url_for("profile")`).
  No behaviour change on failure (form re-renders with the error) or for the
  already-logged-in GET guard.

No brand-new routes. The expense routes (Steps 7–9) remain untouched stubs.

## Database changes
No schema changes. Four new read-only helpers are added to `database/db.py`
(all DB access stays out of the route per project rules), each opening/closing
its own connection in the established `try/finally` style with parameterised
queries:

- `get_user_by_id(user_id)` — return the `users` row (`id`, `name`, `email`,
  `created_at`; `password_hash` deliberately excluded) for the session's
  `user_id`, or `None`.
- `get_expense_summary(user_id)` — return the user's expense count and total
  amount: `SELECT COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total FROM
  expenses WHERE user_id = ?`, so a user with no expenses shows `0` / `₹0`
  rather than `NULL`.
- `get_recent_expenses(user_id, limit=8)` — return the most recent expenses
  (`date`, `category`, `amount`, `description`) ordered `date DESC, id DESC`,
  capped by `limit`, for the recent-transactions list.
- `get_category_breakdown(user_id)` — return per-category `category`, `count`,
  `total` grouped by `category` and ordered `total DESC`, for the
  expenses-by-category card and to derive the top category
  (`breakdown[0]` in the route).

## Templates
- **Create:**
  - `templates/profile.html` — extends `base.html`; a dashboard inside a
    `.profile-page` wrapper with: the account header (`.auth-header` /
    `.auth-title` / `.auth-subtitle` + `.profile-meta` member-since); a
    three-tile `.lp-stats` row (total spent, transactions, top category); and a
    two-column `.profile-grid` of `.profile-card`s — recent transactions
    (`.profile-tx-*`) and expenses by category (`.profile-cat-*` bars). Reuses
    existing `.lp-stat-*` and card patterns; no `{% block head %}`, matching
    existing pages. Includes empty states for a user with no expenses.
- **Modify:**
  - None. `base.html` already links to `url_for('profile')` for logged-in
    users (Step 3), so no navbar change is needed.

## Files to change
- `app.py`
  - Rewrite the `profile` view: redirect to `url_for("login")` if no session
    `user_id`; fetch the user via `get_user_by_id` (clear session + redirect to
    login if it returns `None`); then fetch `get_expense_summary`,
    `get_recent_expenses`, and `get_category_breakdown`, derive
    `top_category = breakdown[0] if breakdown else None`, and render
    `profile.html` with `user`, `summary`, `recent`, `breakdown`,
    `top_category`. Keep the view to one responsibility — fetch data, render.
  - Add `get_category_breakdown`, `get_expense_summary`, `get_recent_expenses`,
    and `get_user_by_id` to the existing `from database.db import (...)` block.
  - In the `login` view, change the successful-login redirect target from
    `url_for("landing")` to `url_for("profile")`.
- `database/db.py`
  - Add the four read-only helpers described under **Database changes**.
- `static/css/style.css`
  - Add the `.profile-*` dashboard styles (wrapper, cards, transaction list,
    category bars) using existing design tokens only.

## Files to create
- `templates/profile.html` — the profile page template.

Note: profile styles are added to the existing `static/css/style.css` (a
`.profile-*` dashboard block — page wrapper, cards, transaction list, category
bars), matching actual codebase practice — no page uses a dedicated CSS file or
`{% block head %}`. This supersedes the earlier "create `static/css/profile.css`"
intent and CLAUDE.md's "page-specific styles → new .css file" wording (stale vs
the codebase).

## New dependencies
No new dependencies. Everything uses Flask (`render_template`, `session`,
`redirect`, `url_for`) and raw `sqlite3` via `get_db()` — all already present.
No additions to `requirements.txt`.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` via `get_db()` only; never inline SQL
  in the route (use the new `database/db.py` helpers).
- Parameterised queries only — `?` placeholders, never f-strings/format in SQL.
- Passwords hashed with werkzeug — never select, render, or expose
  `password_hash` on the profile page.
- Use CSS variables from `style.css` (`--ink`, `--paper-card`, `--accent`,
  etc.) — never hardcode hex values; reuse the existing design tokens and
  `--radius-*` / font variables.
- Amounts are Indian Rupees — display totals with the `₹` symbol, not `$`.
- Use `url_for()` for every internal link — no hardcoded URLs.
- Use `redirect(url_for("login"))` for the not-logged-in case, and `abort()`
  for genuine HTTP errors — never a bare string return.
- All templates extend `base.html`; profile styles live in `style.css`
  (no `{% block head %}`), consistent with every other page.
- Do not implement or alter the expense routes (Steps 7–9); the summary is
  read-only display only.

## Definition of done
- [ ] A successful login (e.g. `demo@spendly.com` / `demo123`) redirects
      straight to `/profile`, landing on the rendered dashboard.
- [ ] Visiting `/profile` while logged out redirects to `/login` (no raw
      string, no stack trace).
- [ ] A stale session (`user_id` set but no matching row) clears the session and
      redirects to `/login` instead of raising a 500.
- [ ] The profile renders `profile.html` extending `base.html` with the navbar
      and footer intact, showing the logged-in user's real name, email, and a
      member-since value derived from `created_at`.
- [ ] The stat row shows the correct **total spent** (with `₹`), **transaction
      count**, and **top category** (name + its total). The demo user shows the
      8 seeded expenses summing to ₹299.49.
- [ ] The **recent transactions** card lists the most recent expenses
      (description/category · date · amount), capped at the helper's limit.
- [ ] The **expenses by category** card lists every category with its total and
      a proportional bar (the top category's bar is full width; no bar exceeds
      100%).
- [ ] A user with no expenses sees total `₹0.00`, count `0`, a `—` top category,
      and empty-state messages in both cards (no `NULL`, no crash, no bars).
- [ ] `password_hash` never appears in the rendered HTML.
- [ ] The `.profile-*` styles in `static/css/style.css` contain no hardcoded
      hex colours (CSS variables only) and the two content cards sit side by
      side on desktop, stacking on narrow screens.
- [ ] No hardcoded internal URLs — all links use `url_for()`.
- [ ] The expense routes (Steps 7–9) remain untouched stubs.
