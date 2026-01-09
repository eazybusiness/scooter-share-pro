# ScooterShare Pro - Enterprise E-Scooter Rental Platform

Enterprise-grade E-Scooter rental platform built with Flask, PostgreSQL, and modern web technologies.

## Features

- **User Management**: Registration, authentication, role-based access control (Admin, Provider, Customer)
- **Scooter Management**: Create, update, delete, and track scooters with real-time location
- **Rental System**: Start, end, and cancel rentals with automatic pricing calculation
- **Payment Processing**: Multiple payment methods with transaction tracking
- **RESTful API**: Comprehensive API with JWT authentication and Swagger documentation
- **Web Interface**: Modern responsive UI built with Bootstrap 5

## Technology Stack

- **Backend**: Python 3.9+, Flask 2.3
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with Flask-JWT-Extended
- **API Documentation**: Flask-RESTX with Swagger UI
- **Frontend**: Jinja2 templates, Bootstrap 5
- **Deployment**: Gunicorn + Nginx

## Architecture

### Design Patterns
- **MVC Pattern**: Clear separation of Models, Views, and Controllers
- **Repository Pattern**: Data access layer abstraction
- **Service Layer**: Business logic encapsulation
- **Blueprint Architecture**: Modular application structure

### Project Structure
```
scooter-share-pro/
├── app/
│   ├── models/          # Database models
│   ├── repositories/    # Data access layer
│   ├── services/        # Business logic
│   ├── api/            # REST API endpoints
│   ├── web/            # Web interface routes
│   ├── templates/      # HTML templates
│   └── static/         # CSS, JS, images
├── migrations/         # Database migrations
├── tests/             # Test suite
├── config.py          # Configuration
├── requirements.txt   # Dependencies
└── run.py            # Application entry point
```

## Installation

### Prerequisites
- Python 3.9 or higher
- PostgreSQL 12 or higher
- pip and virtualenv

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd scooter-share-pro
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your database credentials and secret keys
```

5. Initialize database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. Create admin user:
```bash
flask create-admin
```

## Running the Application

### Development
```bash
python run.py
```

The application will be available at `http://localhost:5000`

### Production with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

### With Nginx (Production)
Configure Nginx as reverse proxy:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## API Documentation

### Authentication
All API endpoints require JWT authentication except registration and login.

#### Register
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe",
  "role": "customer"
}
```

#### Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {...}
}
```

### Using the API
Include the access token in the Authorization header:
```bash
Authorization: Bearer <access_token>
```

### API Endpoints

#### Scooters
- `GET /api/scooters` - List all scooters
- `POST /api/scooters` - Create scooter (Provider/Admin)
- `GET /api/scooters/<id>` - Get scooter details
- `PUT /api/scooters/<id>` - Update scooter
- `DELETE /api/scooters/<id>` - Delete scooter
- `GET /api/scooters/available` - List available scooters
- `GET /api/scooters/nearby?latitude=<lat>&longitude=<lon>` - Find nearby scooters

#### Rentals
- `GET /api/rentals` - List rentals
- `POST /api/rentals` - Start rental
- `GET /api/rentals/<id>` - Get rental details
- `POST /api/rentals/<id>/end` - End rental
- `POST /api/rentals/<id>/cancel` - Cancel rental
- `POST /api/rentals/<id>/rating` - Rate rental

#### Users
- `GET /api/users/me` - Get current user
- `PUT /api/users/me` - Update profile
- `PUT /api/users/me/password` - Change password

### Swagger Documentation
Interactive API documentation available at: `http://localhost:5000/api/docs/`

## Database Schema

### Users
- Email-based authentication
- Role-based access control
- Profile information

### Scooters
- Unique identifier and QR code
- Real-time location tracking
- Battery level monitoring
- Status management (available, in_use, maintenance, offline)

### Rentals
- Start/end timestamps
- Location tracking
- Duration and cost calculation
- Rating system

### Payments
- Multiple payment methods
- Transaction tracking
- Refund support

## Configuration

### Environment Variables
```bash
# Flask
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Database
DATABASE_URL=postgresql://user:password@localhost/scooter_share_pro

# Pricing
BASE_PRICE_PER_MINUTE=0.25
START_FEE=1.0

# Limits
MAX_RENTAL_TIME_HOURS=24
```

## Testing

Run tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=app tests/
```

## Security

- Passwords hashed with bcrypt
- JWT token authentication
- CSRF protection on web forms
- SQL injection prevention via ORM
- Input validation and sanitization

## Performance

- Database indexing on frequently queried fields
- Connection pooling
- Efficient query optimization
- Caching strategies

## Deployment Checklist

- [ ] Set strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Configure production database
- [ ] Set DEBUG=False
- [ ] Configure HTTPS/SSL
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Configure firewall rules

## License

This project is part of an academic assignment for DBWE.TA1A.PA.

## Support

For issues and questions, please contact the development team.
