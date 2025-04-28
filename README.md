# ClimbUp Booking System Backend

A robust booking system backend built with Flask, following a 3-tier architecture design.

## Architecture

- **Client Layer**: Vue.js frontend
- **Middleware**: RESTful API with JWT authentication
- **Server Layer**: Business logic and data services

## Features

- Dynamic pricing based on peak hours and consultant experience
- Real-time availability checking
- Secure payment processing with Redis caching
- Comprehensive logging and error handling
- Modular rule engine for business logic

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- MongoDB 4.4+
- Redis 6.0+

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize databases:
```bash
flask db upgrade
```

## Configuration

Required environment variables:
```env
# Database
POSTGRES_URL=postgresql://user:password@localhost:5432/climbup
MONGO_URL=mongodb://localhost:27017/climbup
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600

# Application
FLASK_ENV=development
FLASK_APP=app.py
```

## API Documentation

### Authentication

- `POST /api/auth/login`: User login
- `POST /api/auth/register`: User registration
- `GET /api/auth/refresh`: Refresh JWT token

### Bookings

- `GET /api/bookings`: List available slots
- `POST /api/bookings`: Create new booking
- `PUT /api/bookings/:id`: Update booking
- `DELETE /api/bookings/:id`: Cancel booking

### Payments

- `POST /api/payments/initiate`: Start payment process
- `POST /api/payments/verify`: Verify payment
- `POST /api/payments/webhook`: Payment webhook endpoint

## Rule Engine

The system uses a modular rule engine for business logic:

1. **Peak Hours**: Dynamic pricing based on time slots
2. **Availability**: Real-time slot availability checking
3. **Pricing**: Complex pricing calculations
4. **Validation**: Booking request validation

## Testing

Run tests with coverage:
```bash
pytest --cov=backend tests/
```

## Deployment

### Docker

Build and run:
```bash
docker-compose up --build
```

### Kubernetes

Deploy to Kubernetes:
```bash
kubectl apply -f k8s/
```

## Monitoring

- Logs are stored in `app.log`
- Error tracking via logging service
- Performance metrics available via `/metrics` endpoint

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details 