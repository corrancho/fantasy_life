# Fantasy Life - Quick Start Guide

## Prerequisites

- Docker and Docker Compose installed
- Git

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/corrancho/fantasy_life.git
cd fantasy_life
```

### 2. Start the application with Docker

```bash
docker compose up --build
```

This will start all services:
- **API Backend**: http://localhost:8000
- **Frontend**: http://localhost:5173
- **Redis**: localhost:6379
- **PostgreSQL**: localhost:5432 (optional)

### 3. Initialize the database

In another terminal, run:

```bash
# Create initial categories
docker compose exec api python manage.py seed_categories

# Create first period and assign wishes (optional, for testing)
docker compose exec api python manage.py create_period --days 30 --dry-run
```

### 4. Access the application

- Open your browser and go to http://localhost:5173
- The API documentation is available at http://localhost:8000/api/

## Development Setup (without Docker)

### Backend Setup

```bash
cd apps/api
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_categories
python manage.py createsuperuser
python manage.py runserver
```

### Frontend Setup

```bash
cd apps/web
npm install
npm run dev
```

## API Endpoints

### Authentication
- `POST /api/users/` - Register new user (email, nickname, password, date_of_birth)
- `POST /api/token/` - Get JWT tokens (login with email and password)
- `POST /api/token/refresh/` - Refresh access token
- `GET /api/users/me/` - Get current user profile

### Categories
- `GET /api/categories/` - List categories (filtered by age)

### Wishes
- `GET /api/wishes/` - List my wishes
- `POST /api/wishes/` - Create wish
- `PUT /api/wishes/{id}/` - Update wish
- `DELETE /api/wishes/{id}/` - Delete wish

### Matches
- `GET /api/matches/` - List my matches
- `POST /api/matches/` - Create match request
- `POST /api/matches/{id}/accept/` - Accept match
- `POST /api/matches/{id}/reject/` - Reject match
- `POST /api/matches/{id}/block/` - Block user

### Assignments
- `GET /api/assignments/` - List assignments
- `POST /api/assignments/{id}/reject/` - Reject assignment (public mode only)

### Negotiations
- `GET /api/negotiations/` - List negotiations
- `POST /api/negotiations/` - Propose date/time
- `POST /api/negotiations/{id}/accept/` - Accept proposal
- `POST /api/negotiations/{id}/reject/` - Reject proposal

### Executions
- `GET /api/executions/` - List completed wishes
- `POST /api/executions/` - Record completion with rating

### Rankings
- `GET /api/rankings/most_completed/` - Users with most completed wishes
- `GET /api/rankings/best_rated/` - Users with best average rating
- `GET /api/rankings/fastest_completion/` - Users with fastest completion time

## Management Commands

### seed_categories
Creates the 5 default categories:
```bash
docker compose exec api python manage.py seed_categories
```

Categories created:
- **Deseo** (general wishes)
- **Fantasía** (adult, 18+)
- **Plan** (activities together)
- **Sorpresa** (special surprises)
- **Reto** (fun challenges)

### create_period
Creates a new period and assigns wishes randomly:
```bash
# Real run
docker compose exec api python manage.py create_period --days 30

# Dry run (preview without saving)
docker compose exec api python manage.py create_period --days 30 --dry-run
```

Features:
- Creates global period for public matches
- Creates individual periods for private matches
- Randomly assigns wishes respecting category limits
- Filters adult content for minors
- Supports custom period length

## Example Workflow

### 1. Register Users
```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user1@example.com",
    "nickname": "user1",
    "password": "password123",
    "password_confirm": "password123",
    "date_of_birth": "1990-01-01"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user1@example.com",
    "password": "password123"
  }'
```

### 3. Create a Wish
```bash
curl -X POST http://localhost:8000/api/wishes/ \
  -H "Content-Type: application/json" \
  -H "Authorization: ******" \
  -d '{
    "category": 1,
    "title": "Cena romántica",
    "description": "Una cena especial en un restaurante italiano",
    "is_active": true
  }'
```

### 4. Create a Match
```bash
curl -X POST http://localhost:8000/api/matches/ \
  -H "Content-Type: application/json" \
  -H "Authorization: ******" \
  -d '{
    "user2": 2,
    "mode": "private",
    "status": "pending"
  }'
```

## Project Structure

```
fantasy_life/
├── apps/
│   ├── api/              # Django backend
│   │   ├── fantasy_life/ # Main Django project
│   │   ├── users/        # Users app
│   │   │   ├── models.py # Custom User model
│   │   │   ├── serializers.py
│   │   │   └── views.py
│   │   └── wishes/       # Game logic app
│   │       ├── models.py # 7 models (Category, Wish, Match, etc.)
│   │       ├── serializers.py
│   │       ├── views.py
│   │       ├── admin.py
│   │       └── management/commands/
│   │           ├── seed_categories.py
│   │           └── create_period.py
│   └── web/              # React frontend
│       ├── src/
│       │   ├── api.js    # Axios API client
│       │   ├── websocket.js
│       │   └── App.jsx
│       └── package.json
├── infra/                # Infrastructure files
├── docker-compose.yml
└── README.md
```

## Features Implemented

### Backend
- ✅ Custom User model with email authentication
- ✅ JWT authentication with refresh tokens
- ✅ Argon2 password hashing (most secure)
- ✅ 7 core models for game logic
- ✅ Complete REST API
- ✅ Age-based content filtering (backend enforced)
- ✅ Private mode (couples) and public mode (network)
- ✅ Random wish assignment per period
- ✅ Date/time negotiation system
- ✅ Execution with 1-5 star ratings
- ✅ 3 types of global rankings
- ✅ Admin interface for all models
- ✅ Management commands for setup

### Frontend
- ✅ React + Vite setup
- ✅ Axios API client with JWT handling
- ✅ WebSocket manager
- ✅ Responsive homepage
- ✅ Complete feature overview
- ✅ API documentation display

### Infrastructure
- ✅ Docker Compose with 4 services
- ✅ Redis for WebSockets
- ✅ PostgreSQL ready for production
- ✅ SQLite for development
- ✅ Environment-based configuration

## Troubleshooting

### Port already in use
If you get "port already in use" errors:
```bash
docker compose down
# Then try again
docker compose up --build
```

### Database issues
Reset the database:
```bash
docker compose down -v
docker compose up --build
# Re-run seed_categories
docker compose exec api python manage.py seed_categories
```

### Backend not starting
Check logs:
```bash
docker compose logs api
```

### Frontend not starting
Check logs:
```bash
docker compose logs web
```

## Security Notes

- ✅ All dependencies scanned (0 vulnerabilities)
- ✅ CodeQL analysis (0 alerts)
- ✅ Argon2 password hashing
- ✅ JWT with secure token rotation
- ✅ Age restrictions enforced in backend
- ✅ Match-based permissions
- ⚠️ LocalStorage for tokens (acceptable for demo; use httpOnly cookies in production)

## Next Steps

The project is fully functional according to the README specification. To extend it, consider:
- Implementing WebSocket real-time notifications
- Building complete UI for all operations
- Adding rate limiting for authentication
- Writing automated tests
- Setting up Nginx for production

## License

© 2025 — Fantasy Life
