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

### 3. Access the application

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
- `POST /api/token/` - Get JWT tokens (login)
- `POST /api/token/refresh/` - Refresh access token

### Users
- `POST /api/users/` - Register new user
- `GET /api/users/me/` - Get current user profile
- `GET /api/users/` - List users (authenticated)

## Environment Variables

Copy `.env.example` to `.env` and adjust as needed:

```bash
cp .env.example .env
```

## Project Structure

```
fantasy_life/
├── apps/
│   ├── api/              # Django backend
│   │   ├── fantasy_life/ # Main Django project
│   │   ├── users/        # Users app
│   │   ├── manage.py
│   │   └── requirements.txt
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
- ✅ Argon2 password hashing
- ✅ Django REST Framework setup
- ✅ Django Channels configuration
- ✅ CORS configuration
- ✅ Redis integration for WebSockets
- ✅ SQLite (dev) / PostgreSQL (prod) support

### Frontend
- ✅ React + Vite setup
- ✅ Axios API client with JWT handling
- ✅ WebSocket manager
- ✅ Basic UI layout

## Next Steps

The basic infrastructure is ready. Next phase includes:

1. **Core Models**: Wishes, Categories, Matches, Periods
2. **Game Logic**: Wish assignment, negotiation, scoring
3. **WebSocket Features**: Real-time notifications
4. **Privacy Controls**: Fine-grained permission system
5. **Rankings**: Leaderboards and statistics
6. **UI Components**: Complete user interface

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
```

## License

© 2025 — Fantasy Life
