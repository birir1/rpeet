# KCK API — Kenya Community in Korea

REST API backend for the Kenya Community in Korea (KCK) platform. Handles member registration, membership management, leadership roles, official communications, event management, certificate generation, and analytics.

**Author:** Meshack Tirop (Tirop Meshack Kimutai)

---

## Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.12+ |
| Framework | Django | 6.0 |
| API | Django REST Framework | 3.15 |
| Database | PostgreSQL (prod) / SQLite (dev) | 15+ |
| Auth | JWT (SimpleJWT) | 5.3+ |
| Task Queue | Celery + Redis | 5.3+ |
| Image Gen | Pillow | 10.2+ |
| PDF Gen | WeasyPrint | 62.0+ |
| QR Codes | qrcode | 7.4+ |
| Error Tracking | Sentry SDK | 2.0+ |

---

## Project Structure

```
backend/
├── kck_api/                          # Django project configuration
│   ├── settings/
│   │   ├── base.py                   # Development settings (SQLite, DEBUG=True)
│   │   └── production.py             # Production overrides (PostgreSQL, HTTPS, Sentry)
│   ├── celery.py                     # Celery app + beat schedule
│   ├── urls.py                       # Root URL config + health check
│   └── wsgi.py                       # WSGI entry point
│
├── apps/                             # Django applications
│   ├── users/                        # User accounts, memberships, audit logs
│   │   ├── models.py                 # User (custom, email-based), Membership, AuditLog
│   │   ├── views.py                  # Auth, user CRUD, membership, password reset
│   │   ├── serializers.py            # Registration, profile, membership serializers
│   │   ├── urls_auth.py              # /kck/auth/* routes
│   │   ├── urls_memberships.py       # /kck/memberships/* routes
│   │   ├── tasks.py                  # Nightly membership expiry task
│   │   ├── admin.py                  # Django admin configuration
│   │   └── tests/                    # 20 tests (models + views)
│   │
│   ├── leaders/                      # Leadership roles & permissions
│   │   ├── models.py                 # Leader, LeaderPermission (granular flags)
│   │   ├── views.py                  # CRUD, permission management
│   │   ├── serializers.py            # Leader profile serializers
│   │   └── tests/                    # 7 tests
│   │
│   ├── communications/               # Official letters & announcements
│   │   ├── models.py                 # Communication, Announcement
│   │   ├── views.py                  # CRUD, PDF/image download, bulk email, WhatsApp share
│   │   ├── tasks.py                  # Async image/PDF generation, bulk email sending
│   │   └── tests/                    # 8 tests
│   │
│   ├── events/                       # Event management
│   │   ├── models.py                 # Event, EventAttendee, EventPhoto
│   │   ├── views.py                  # CRUD, publish, photos, attendees, batch certificates
│   │   ├── serializers.py            # List/detail/create serializers
│   │   └── tests/                    # 8 tests
│   │
│   ├── certificates/                 # Certificate generation & verification
│   │   ├── models.py                 # Certificate (with QR code, verification URL)
│   │   ├── views.py                  # Create, status polling, download, public verify
│   │   ├── tasks.py                  # Async image/PDF/QR generation (Pillow)
│   │   └── tests/                    # 8 tests
│   │
│   ├── analytics/                    # Dashboard statistics & site settings
│   │   ├── models.py                 # SiteSetting (key-value config store)
│   │   ├── views.py                  # Overview, city/category breakdowns, membership stats
│   │   └── tests/                    # 7 tests
│   │
│   └── common/                       # Shared utilities
│       ├── permissions.py            # Role-based permission classes
│       ├── renderers.py              # KCKRenderer (API envelope), exception handler
│       ├── pagination.py             # KCKPagination (25/page, max 100)
│       ├── audit.py                  # Centralized audit logging
│       └── views.py                  # Image upload endpoint (CKEditor)
│
├── deploy/                           # Deployment configuration
│   ├── docker-compose.yml            # Full stack (Postgres, Redis, Django, Celery, Nginx)
│   ├── .env.example                  # Environment variable template
│   ├── Dockerfile.frontend           # Laravel frontend image
│   ├── nginx/                        # Nginx configs (HTTP + SSL)
│   └── scripts/setup-hetzner.sh      # One-time server setup
│
├── Dockerfile                        # Backend Docker image
├── .dockerignore
├── .github/workflows/ci.yml          # CI/CD pipeline (test -> build -> deploy)
├── requirements/base.txt             # Python dependencies
├── conftest.py                       # Shared pytest fixtures
├── manage.py
└── pytest.ini
```

---

## Quick Start (Development)

### Prerequisites
- Python 3.12+
- Redis (for Celery, or run with `CELERY_TASK_ALWAYS_EAGER=True`)

### Setup

```bash
# Clone and enter
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements/base.txt

# Run migrations
python manage.py migrate

# Seed test data (optional)
python manage.py seed_data

# Start server
python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000/kck/`.

### Default Test Accounts (after seed_data)

| Role | Email | Password |
|------|-------|----------|
| Chairman | chairman@kck.or.ke | Chairman@2025 |
| Secretary | secretary@kck.or.ke | Secretary@2025 |
| Treasurer | treasurer@kck.or.ke | Treasurer@2025 |
| Welfare | welfare@kck.or.ke | Welfare@2025 |
| Committee | committee@kck.or.ke | Committee@2025 |

---

## API Reference

All endpoints return a consistent envelope:
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/kck/auth/register/` | Public | Register new user |
| POST | `/kck/auth/login/` | Public | Login, returns JWT tokens |
| POST | `/kck/auth/token/refresh/` | Public | Refresh access token |
| POST | `/kck/auth/logout/` | JWT | Blacklist refresh token |
| GET | `/kck/auth/me/` | JWT | Current user profile |
| POST | `/kck/auth/password-reset/` | Public | Request password reset email |
| POST | `/kck/auth/password-reset/confirm/` | Public | Set new password with token |
| GET | `/kck/auth/verify-email/{token}/` | Public | Verify email address |

### Users

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/kck/users/` | Secretary | List all users (paginated, filterable) |
| GET | `/kck/users/{id}/` | Owner/Secretary | User detail |
| PUT | `/kck/users/{id}/update/` | Owner/Secretary | Update user profile |
| POST | `/kck/users/{id}/verify/` | Secretary | Verify user account |
| POST | `/kck/users/bulk-verify/` | Secretary | Bulk verify (max 100) |
| DELETE | `/kck/users/{id}/delete/` | Chairman | Soft delete user |
| GET | `/kck/users/export/` | Secretary | Download CSV export |
| GET | `/kck/users/map-data/` | Secretary | City distribution data |

### Memberships

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/kck/memberships/` | Treasurer | List all memberships (paginated) |
| POST | `/kck/memberships/` | Treasurer | Create membership record |
| GET | `/kck/memberships/mine/` | JWT | Current user's membership |
| POST | `/kck/memberships/request/` | JWT | User requests membership |
| GET | `/kck/memberships/{id}/` | Treasurer | Membership detail |
| PUT | `/kck/memberships/{id}/` | Treasurer | Update membership |
| POST | `/kck/memberships/{id}/renew/` | Treasurer | Extend by 1 year (in-place) |
| GET | `/kck/memberships/report/` | Treasurer | Financial summary |

### Leaders

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/kck/leaders/` | Public | List active leaders |
| POST | `/kck/leaders/create/` | Chairman | Appoint leader |
| PUT | `/kck/leaders/me/` | Any Leader | Update own profile |
| PUT | `/kck/leaders/{id}/` | Chairman | Update leader |
| POST | `/kck/leaders/{id}/deactivate/` | Chairman | Deactivate leader |
| GET/PUT | `/kck/leaders/{id}/permissions/` | Chairman | Manage granular permissions |

### Communications

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/kck/comms/` | JWT | List communications (paginated) |
| POST | `/kck/comms/create/` | Any Leader | Create (triggers async PDF/image) |
| GET | `/kck/comms/public/` | Public | Published communications |
| GET | `/kck/comms/{id}/` | Public/JWT | Communication detail |
| PUT | `/kck/comms/{id}/update/` | Any Leader | Update |
| DELETE | `/kck/comms/{id}/delete/` | Any Leader | Delete |
| GET | `/kck/comms/{id}/status/` | JWT | Check generation progress |
| GET | `/kck/comms/{id}/pdf/` | JWT | Download PDF |
| GET | `/kck/comms/{id}/image/` | JWT | Download image |
| GET | `/kck/comms/{id}/share-image/` | Public | WhatsApp share link |
| POST | `/kck/comms/bulk-email/` | Any Leader | Send bulk email (max 500) |

### Announcements

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/kck/announcements/` | Public | Published announcements |
| GET | `/kck/announcements/{id}/` | Public | Announcement detail |
| GET | `/kck/announcements/manage/` | Any Leader | All (including drafts) |
| POST | `/kck/announcements/create/` | Any Leader | Create |
| PUT | `/kck/announcements/{id}/update/` | Any Leader | Update |
| DELETE | `/kck/announcements/{id}/delete/` | Any Leader | Delete |

### Events

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/kck/events/` | Public | Published events (paginated) |
| GET | `/kck/events/{slug}/` | Public | Event detail by slug |
| POST | `/kck/events/create/` | Committee | Create event |
| GET | `/kck/events/{id}/detail/` | Committee | Event detail (includes drafts) |
| PUT | `/kck/events/{id}/update/` | Committee | Update event |
| POST | `/kck/events/{id}/publish/` | Committee | Publish event |
| POST | `/kck/events/{id}/photos/` | Committee | Upload gallery photo |
| DELETE | `/kck/events/{id}/photos/{photo_id}/` | Committee | Delete photo |
| GET/POST | `/kck/events/{id}/attendees/` | Committee | Manage attendees |
| POST | `/kck/events/{id}/batch-certs/` | Committee | Generate certs for all attendees |
| DELETE | `/kck/events/{id}/delete/` | Committee | Delete event |

### Certificates

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/kck/certs/` | Any Leader | List certificates (paginated) |
| POST | `/kck/certs/create/` | Any Leader | Create (async generation) |
| GET | `/kck/certs/mine/` | JWT | Current user's certificates |
| GET | `/kck/certs/{id}/` | JWT | Certificate detail |
| GET | `/kck/certs/{id}/status/` | JWT | Generation progress (polling) |
| GET | `/kck/certs/{id}/pdf/` | JWT | Download PDF |
| GET | `/kck/certs/{id}/image/` | JWT | Download image |
| GET | `/kck/certs/verify/{cert_number}/` | Public | Verify certificate authenticity |

### Analytics & Settings

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/kck/analytics/overview/` | Public/Chairman | Dashboard statistics |
| GET | `/kck/analytics/cities/` | Secretary | City breakdown |
| GET | `/kck/analytics/categories/` | Secretary | Category breakdown |
| GET | `/kck/analytics/membership/` | Treasurer | Membership statistics |
| GET/PUT | `/kck/settings/membership-fee/` | Public/Chairman | Membership fee config |

### Utility

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health/` | Public | Health check (DB connectivity) |
| POST | `/kck/media/upload/` | JWT | Image upload (CKEditor) |

---

## Authentication Flow

```
POST /kck/auth/login/  { email, password }
  -> { access: "eyJ...", refresh: "eyJ...", user: {...} }

# Use access token for all authenticated requests:
GET /kck/users/
  Authorization: Bearer eyJ...

# When access token expires (15min prod / 24hr dev):
POST /kck/auth/token/refresh/  { refresh: "eyJ..." }
  -> { access: "new-eyJ..." }

# Logout (blacklists refresh token):
POST /kck/auth/logout/  { refresh: "eyJ..." }
```

---

## Role & Permission System

### Roles (hierarchy)
```
Chairman ──> full access to everything
Secretary -> user management, verification, exports
Treasurer -> membership & financial management
Welfare ──> welfare case management
Committee -> event management
```

Each leader also has a `LeaderPermission` record with 10 granular boolean flags that the chairman can override:
- `can_manage_users`, `can_verify_users`, `can_export_users`
- `can_manage_memberships`, `can_view_financials`
- `can_send_communications`, `can_issue_certificates`
- `can_manage_events`, `can_manage_leaders`, `can_view_analytics`

---

## Membership Renewal

Renewals are handled **in-place** on the same record (no duplicates):

```
POST /kck/memberships/{id}/renew/
```

- If membership is still active (expiry in future): extends from current expiry date
- If membership is expired: extends from today
- Increments `renewal_count`
- Appends to `renewal_history` JSON array for audit trail
- Sets status back to `active`

Example `renewal_history`:
```json
[
  {
    "date": "2026-03-28",
    "extended_from": "2027-01-24",
    "extended_to": "2028-01-24",
    "by": "James Mwangi"
  }
]
```

---

## Async Tasks (Celery)

| Task | Schedule | Description |
|------|----------|-------------|
| `expire_memberships_task` | Daily @ 1:00 AM | Marks expired memberships |
| `refresh_analytics_cache` | Every 15 minutes | Refreshes cached statistics |
| `generate_comm_image_task` | On demand | Renders communication letterhead image |
| `generate_comm_pdf_task` | On demand | Generates communication PDF |
| `send_bulk_email_task` | On demand | Sends HTML emails to recipients |
| `generate_cert_image_task` | On demand | Renders certificate image (A4 landscape) |
| `generate_cert_pdf_task` | On demand | Converts certificate to PDF |
| `generate_qr_task` | On demand | Generates QR code for verification |

---

## Testing

```bash
# Run all tests
python -m pytest

# Run specific app
python -m pytest apps/users/

# Run with coverage
python -m pytest --cov=apps --cov-report=term-missing
```

**Current:** 58 tests passing across all apps.

---

## Deployment

### Docker (Production)

```bash
cd deploy
cp .env.example .env    # fill in real values
docker compose up -d

# Run initial migrations
docker compose run --rm backend python manage.py migrate
docker compose run --rm backend python manage.py createsuperuser
```

### CI/CD

Push to `main` triggers the GitHub Actions pipeline:
1. **Test** — runs pytest against PostgreSQL
2. **Build** — builds Docker image, pushes to GitHub Container Registry
3. **Deploy** — SSHs to Hetzner, pulls image, runs migrations, restarts containers, verifies health check

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `HETZNER_HOST` | Server IP address |
| `HETZNER_USER` | SSH user (deploy) |
| `HETZNER_SSH_KEY` | Private SSH key |

### Environment Variables

See `deploy/.env.example` for the complete list. Key variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `DJANGO_SECRET_KEY` | Yes | Django secret key |
| `DB_PASSWORD` | Yes | PostgreSQL password |
| `DJANGO_ALLOWED_HOSTS` | Yes | Comma-separated domains |
| `CORS_ALLOWED_ORIGINS` | Yes | Comma-separated origins |
| `EMAIL_HOST_USER` | Yes | SMTP email address |
| `EMAIL_HOST_PASSWORD` | Yes | SMTP app password |
| `SENTRY_DSN` | No | Sentry error tracking DSN |
| `KCK_BASE_URL` | No | Base URL for certificate verification links |

---

## Architecture Decisions

- **UUID primary keys** — distributed-system compatible, no sequential ID leaking
- **Email-based auth** — no usernames, email is the natural identifier for this community
- **Soft delete on users** — preserves audit trail and membership history
- **JWT with rotation** — stateless auth, refresh token rotation for security
- **Celery for heavy work** — PDF/image generation takes 2-5 seconds, too slow for sync
- **Custom API envelope** — every response wrapped in `{success, data, error}` for consistent frontend handling
- **In-place membership renewal** — one record per member, renewal_history JSON for audit (no duplicate rows)
- **Bleach HTML sanitization** — user-generated content (announcements, events, comms) is sanitized on input
- **Rate limiting** — auth endpoints rate-limited to prevent brute force (disabled in dev/test)

---

## Project Stats

| Metric | Count |
|--------|-------|
| Django apps | 7 |
| API endpoints | 70+ |
| Source files | 68 |
| Lines of code | ~6,500 |
| Tests | 58 |
| Database migrations | 53 |

---

## License

Private. Kenya Community in Korea (KCK).
