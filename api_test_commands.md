# Scooter Share Pro API Test Commands

## 🚀 API Testing Guide

This document contains all the curl commands to test the Scooter Share Pro API after deployment.

### Base URL
```
https://scooter-share-pro.onrender.com
```

### API Documentation
```
https://scooter-share-pro.onrender.com/api/docs/
```

## 📋 Test Commands

### 1. API Documentation
```bash
curl -X GET https://scooter-share-pro.onrender.com/api/docs/ \
  -H "Content-Type: application/html"
```

### 2. User Registration
```bash
curl -X POST https://scooter-share-pro.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "first_name": "Test",
    "last_name": "User",
    "role": "customer"
  }'
```

**Expected Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "role": "customer"
  }
}
```
**Status Code:** 201

### 3. User Login
```bash
curl -X POST https://scooter-share-pro.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "role": "customer"
  }
}
```

### 4. Get All Scooters (Requires Auth)
```bash
# Replace YOUR_TOKEN with the access token from login
curl -X GET https://scooter-share-pro.onrender.com/api/scooters/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "scooters": [
    {
      "id": 1,
      "identifier": "SC-001-AB",
      "model": "Xiaomi Mi Electric Scooter Pro 2",
      "status": "available",
      "battery_level": 85,
      "location": "Hauptbahnhof Zürich",
      "latitude": 47.3769,
      "longitude": 8.5417
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10
}
```

### 5. Get Available Scooters (Requires Auth)
```bash
curl -X GET https://scooter-share-pro.onrender.com/api/scooters/available \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. Get Specific Scooter (Requires Auth)
```bash
curl -X GET https://scooter-share-pro.onrender.com/api/scooters/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 7. Get Nearby Scooters (Requires Auth)
```bash
curl -X GET "https://scooter-share-pro.onrender.com/api/scooters/nearby?latitude=47.3769&longitude=8.5417&radius=5" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 8. Get User Rentals (Requires Auth)
```bash
curl -X GET https://scooter-share-pro.onrender.com/api/rentals/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "rentals": [
    {
      "id": 1,
      "rental_code": "SC-2026-001",
      "scooter": {
        "id": 1,
        "identifier": "SC-001-AB",
        "model": "Xiaomi Mi Electric Scooter Pro 2"
      },
      "start_time": "2026-01-10T11:09:23.123456",
      "end_time": null,
      "status": "active",
      "total_cost": null,
      "duration_minutes": 5
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10
}
```

### 9. Get Rental Statistics (Requires Auth)
```bash
curl -X GET https://scooter-share-pro.onrender.com/api/rentals/statistics \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "total_rentals": 5,
  "completed_rentals": 4,
  "active_rentals": 1,
  "total_spent": 25.50,
  "average_duration": 12.5,
  "favorite_scooter": "Xiaomi Mi Electric Scooter Pro 2"
}
```

### 10. Start Rental (Requires Auth)
```bash
curl -X POST https://scooter-share-pro.onrender.com/api/rentals/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "scooter_id": 1,
    "start_latitude": 47.3769,
    "start_longitude": 8.5417
  }'
```

**Expected Response:**
```json
{
  "message": "Rental started successfully",
  "rental": {
    "id": 2,
    "rental_code": "SC-2026-002",
    "scooter": {
      "id": 1,
      "identifier": "SC-001-AB",
      "model": "Xiaomi Mi Electric Scooter Pro 2"
    },
    "start_time": "2026-01-10T11:15:23.123456",
    "status": "active"
  }
}
```
**Status Code:** 201

### 11. End Rental (Requires Auth)
```bash
curl -X POST https://scooter-share-pro.onrender.com/api/rentals/1/end \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "end_latitude": 47.3780,
    "end_longitude": 8.5400
  }'
```

**Expected Response:**
```json
{
  "message": "Rental ended successfully",
  "rental": {
    "id": 1,
    "end_time": "2026-01-10T11:20:23.123456",
    "total_cost": 2.70,
    "duration_minutes": 5,
    "status": "completed"
  }
}
```

### 12. Cancel Rental (Requires Auth)
```bash
curl -X POST https://scooter-share-pro.onrender.com/api/rentals/1/cancel \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "reason": "Customer request"
  }'
```

### 13. Get User Profile (Requires Auth)
```bash
curl -X GET https://scooter-share-pro.onrender.com/api/users/me \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "id": 1,
  "email": "test@example.com",
  "first_name": "Test",
  "last_name": "User",
  "role": "customer",
  "is_active": true,
  "created_at": "2026-01-10T10:00:00",
  "rentals_count": 5,
  "total_spent": 25.50
}
```

### 14. Update User Profile (Requires Auth)
```bash
curl -X PUT https://scooter-share-pro.onrender.com/api/users/me \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "first_name": "Updated",
    "last_name": "Name"
  }'
```

### 15. Refresh Token (Requires Auth)
```bash
curl -X POST https://scooter-share-pro.onrender.com/api/auth/refresh \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_REFRESH_TOKEN"
```

## 🔧 Error Testing

### Invalid Login
```bash
curl -X POST https://scooter-share-pro.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invalid@example.com",
    "password": "wrongpassword"
  }'
```

**Expected Response:**
```json
{
  "error": "Invalid credentials"
}
```
**Status Code:** 401

### Unauthorized Access
```bash
curl -X GET https://scooter-share-pro.onrender.com/api/scooters/ \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "error": "Authorization required"
}
```
**Status Code:** 401

### Invalid Endpoint
```bash
curl -X GET https://scooter-share-pro.onrender.com/api/invalid \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "error": "Not found"
}
```
**Status Code:** 404

## 📱 Mobile App Integration

For mobile app development, use these endpoints:

### Authentication Flow
1. **Register:** `POST /api/auth/register` - Create new user
2. **Login:** `POST /api/auth/login` - Get JWT tokens
3. **Refresh:** `POST /api/auth/refresh` - Refresh access token
4. **Include token** in all subsequent requests: `Authorization: Bearer TOKEN`

### Core Features
1. **Browse Scooters:** `GET /api/scooters/available`
2. **Find Nearby:** `GET /api/scooters/nearby?lat=X&lng=Y&radius=Z`
3. **Start Rental:** `POST /api/rentals/`
4. **End Rental:** `POST /api/rentals/{id}/end`
5. **View History:** `GET /api/rentals/`
6. **User Stats:** `GET /api/rentals/statistics`

### Response Format
All responses are in JSON format with appropriate HTTP status codes:
- `200` - Success
- `201` - Created (for new resources)
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

## 🧪 Automated Testing

Run the automated test suite:
```bash
python3 test_api.py
```

This will test all endpoints and generate a detailed report.

## 📊 API Documentation

### Endpoints Summary

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/docs/` | No | Swagger API Documentation |
| POST | `/api/auth/register` | No | User registration |
| POST | `/api/auth/login` | No | User authentication |
| POST | `/api/auth/refresh` | Yes | Refresh JWT token |
| GET | `/api/auth/me` | Yes | Get current user info |
| GET | `/api/scooters/` | Yes | List all scooters |
| GET | `/api/scooters/available` | Yes | List available scooters |
| GET | `/api/scooters/{id}` | Yes | Get scooter details |
| GET | `/api/scooters/nearby` | Yes | Find nearby scooters |
| GET | `/api/rentals/` | Yes | List user rentals |
| GET | `/api/rentals/{id}` | Yes | Get rental details |
| POST | `/api/rentals/` | Yes | Start new rental |
| POST | `/api/rentals/{id}/end` | Yes | End rental |
| POST | `/api/rentals/{id}/cancel` | Yes | Cancel rental |
| GET | `/api/rentals/statistics` | Yes | User rental statistics |
| GET | `/api/users/me` | Yes | Get user profile |
| PUT | `/api/users/me` | Yes | Update user profile |

### Data Models

#### Scooter
```json
{
  "id": 1,
  "identifier": "SC-001-AB",
  "model": "Scooter Model",
  "status": "available|in_use|maintenance",
  "battery_level": 85,
  "location": "Location",
  "latitude": 47.3769,
  "longitude": 8.5417,
  "created_at": "2026-01-10T10:00:00"
}
```

#### Rental
```json
{
  "id": 1,
  "rental_code": "SC-2026-001",
  "scooter": {...},
  "start_time": "2026-01-10T11:00:00",
  "end_time": "2026-01-10T11:15:00",
  "status": "active|completed|cancelled",
  "total_cost": 2.70,
  "duration_minutes": 15,
  "start_latitude": 47.3769,
  "start_longitude": 8.5417,
  "end_latitude": 47.3780,
  "end_longitude": 8.5400
}
```

#### User
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "First",
  "last_name": "Last",
  "role": "customer|provider|admin",
  "is_active": true,
  "created_at": "2026-01-10T10:00:00",
  "rentals_count": 5,
  "total_spent": 25.50
}
```

## 🚨 Troubleshooting

### Common Issues

1. **401 Unauthorized**: Check JWT token is valid and included in headers
2. **404 Not Found**: Verify endpoint URL is correct
3. **500 Internal Error**: Check server logs for detailed error information

### Debug Tips

1. Use `-v` flag with curl for verbose output:
   ```bash
   curl -v -X GET https://scooter-share-pro.onrender.com/api/scooters/available
   ```

2. Check response headers:
   ```bash
   curl -I https://scooter-share-pro.onrender.com/api/scooters/available
   ```

3. Pretty print JSON responses:
   ```bash
   curl ... | python3 -m json.tool
   ```

## 📞 Support

For API issues or questions:
1. Check the Swagger documentation at `/api/docs/`
2. Review the automated test suite results
3. Check server logs for detailed error information
4. Verify JWT token format and expiration
