# Contributing to Scooter-Share-Pro

Willkommen bei Scooter-Share-Pro! Wir freuen uns über Ihren Beitrag zu unserer Enterprise E-Scooter Sharing Plattform.

## 🚀 Quick Start

### Voraussetzungen
- Docker Desktop 4.0+
- Kubernetes 1.28+
- kubectl
- Helm 3.0+
- Go 1.21+ (für Services)
- Node.js 18+ (für Frontend)

### Lokale Entwicklung einrichten

1. **Repository klonen**
```bash
git clone https://github.com/eazybusiness/scooter-share-pro.git
cd scooter-share-pro
```

2. **Docker-Stack starten**
```bash
# Development Umgebung
docker-compose -f docker-compose.dev.yml up -d

# Kubernetes (optional)
kubectl apply -f k8s/development/
```

3. **Services bauen**
```bash
# Backend Services
make build-services

# Frontend
make build-frontend

# Alle Komponenten
make build-all
```

4. **Datenbank initialisieren**
```bash
# PostgreSQL Migrations
make migrate-db

# Testdaten laden
make seed-db
```

5. **Zugriff auf Services**
- API Gateway: http://localhost:8080
- Admin Dashboard: http://localhost:3000
- Grafana Monitoring: http://localhost:3001

## 📋 Development Workflow

### 1. Feature Branch erstellen
```bash
git checkout -b feature/user-authentication
# oder
git checkout -b fix/payment-gateway-issue
```

### 2. Entwicklungsumgebung
```bash
# Development Stack starten
make dev-up

# Logs anzeigen
make logs SERVICE=user-service

# Service neu starten
make restart SERVICE=scooter-service
```

### 3. Code Quality prüfen
```bash
# Go Services
make lint-go
make test-go
make security-scan

# Frontend
make lint-frontend
make test-frontend
make build-frontend

# Infrastructure
make lint-k8s
make validate-helm
```

### 4. Integration Tests
```bash
# End-to-End Tests
make e2e-test

# Load Testing
make load-test

# Security Tests
make security-test
```

### 5. Commit erstellen
```bash
git add .
git commit -m "feat(user): Add JWT authentication with refresh tokens"
```

### 6. Pull Request
```bash
git push origin feature/user-authentication
# PR auf GitHub erstellen
```

## 🏗️ Projektstruktur

```
scooter-share-pro/
├── services/               # Microservices
│   ├── user-service/      # User Management
│   ├── scooter-service/   # Fleet Management
│   ├── rental-service/    # Rental Processing
│   ├── payment-service/   # Payment Processing
│   └── notification-service/
├── frontend/              # React Admin Dashboard
├── mobile/                # React Native Apps
├── infrastructure/        # Kubernetes & Helm
│   ├── k8s/              # Kubernetes Manifests
│   ├── helm/             # Helm Charts
│   └── terraform/        # Cloud Resources
├── shared/               # Shared Libraries
│   ├── proto/            # gRPC Definitions
│   ├── config/           # Configuration
│   └── monitoring/       # Dashboards
├── tests/                # Test Suites
│   ├── unit/             # Unit Tests
│   ├── integration/      # Integration Tests
│   └── e2e/              # End-to-End Tests
└── docs/                 # Documentation
```

## 🧪 Testing Guidelines

### Test-Pyramide

1. **Unit Tests (70%)**: Schnelle, isolierte Tests
2. **Integration Tests (20%)**: Service-Interaktionen
3. **E2E Tests (10%)**: Komplette User-Workflows

### Go Service Tests

```go
// services/user-service/internal/handler/user_test.go
package handler

import (
    "context"
    "net/http"
    "net/http/httptest"
    "testing"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
    "github.com/scooter-share-pro/user-service/internal/service"
)

func TestCreateUserHandler(t *testing.T) {
    // Arrange
    mockService := &service.MockUserService{}
    handler := NewUserHandler(mockService)
    
    expectedUser := &service.User{
        ID:    "user-123",
        Email: "test@example.com",
        Name:  "Test User",
    }
    
    mockService.On("CreateUser", mock.Anything, mock.Anything).
        Return(expectedUser, nil)
    
    payload := `{
        "email": "test@example.com",
        "name": "Test User",
        "password": "securepassword123"
    }`
    
    req := httptest.NewRequest("POST", "/users", strings.NewReader(payload))
    req.Header.Set("Content-Type", "application/json")
    
    // Act
    rr := httptest.NewRecorder()
    handler.CreateUser(rr, req)
    
    // Assert
    assert.Equal(t, http.StatusCreated, rr.Code)
    
    var response map[string]interface{}
    err := json.Unmarshal(rr.Body.Bytes(), &response)
    assert.NoError(t, err)
    assert.Equal(t, "user-123", response["id"])
    assert.Equal(t, "test@example.com", response["email"])
    
    mockService.AssertExpectations(t)
}
```

### Integration Tests

```go
// tests/integration/rental_flow_test.go
package integration

import (
    "context"
    "testing"
    "time"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/suite"
    "github.com/scooter-share-pro/tests/testcontainers"
)

type RentalFlowTestSuite struct {
    suite.Suite
    containers *testcontainers.TestContainers
    baseURL    string
}

func (suite *RentalFlowTestSuite) SetupSuite() {
    suite.containers = testcontainers.New()
    suite.baseURL = suite.containers.GetAPIGatewayURL()
}

func (suite *RentalFlowTestSuite) TestCompleteRentalFlow() {
    // Arrange
    client := NewAPIClient(suite.baseURL)
    
    // User registrieren
    user := client.RegisterUser("test@example.com", "password123")
    token := client.Login("test@example.com", "password123")
    
    // Scooter erstellen
    scooter := client.CreateScooter("SC001", "Xiaomi", "Mi Pro")
    
    // Act
    rental := client.StartRental(scooter.ID, token)
    
    // Simulate rental time
    time.Sleep(2 * time.Second)
    
    endedRental := client.EndRental(rental.ID, token)
    
    // Assert
    assert.NotNil(suite.T(), user.ID)
    assert.NotNil(suite.T(), scooter.ID)
    assert.NotNil(suite.T(), rental.ID)
    assert.Equal(suite.T(), "completed", endedRental.Status)
    assert.Greater(suite.T(), endedRental.TotalCost, 0.0)
}

func TestRentalFlowSuite(t *testing.T) {
    suite.Run(t, new(RentalFlowTestSuite))
}
```

### Frontend Tests

```javascript
// frontend/src/components/__tests__/ScooterMap.test.jsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import ScooterMap from '../ScooterMap';
import scooterSlice from '../../store/slices/scooterSlice';

const createTestStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      scooters: scooterSlice,
    },
    preloadedState: initialState,
  });
};

const mockScooters = [
  {
    id: 'scooter-1',
    identifier: 'SC001',
    location: { latitude: 52.520008, longitude: 13.404954 },
    status: 'available',
    batteryLevel: 85,
  },
];

describe('ScooterMap', () => {
  const renderWithProviders = (component, initialState = {}) => {
    const store = createTestStore({ scooters: { scooters: mockScooters } });
    return render(
      <Provider store={store}>
        <BrowserRouter>
          {component}
        </BrowserRouter>
      </Provider>
    );
  };

  test('renders scooters on map', async () => {
    renderWithProviders(<ScooterMap />);
    
    await waitFor(() => {
      expect(screen.getByTestId('scooter-marker-scooter-1')).toBeInTheDocument();
    });
  });

  test('shows scooter info on marker click', async () => {
    renderWithProviders(<ScooterMap />);
    
    await waitFor(() => {
      const marker = screen.getByTestId('scooter-marker-scooter-1');
      fireEvent.click(marker);
    });
    
    expect(screen.getByText('SC001')).toBeInTheDocument();
    expect(screen.getByText('85% battery')).toBeInTheDocument();
    expect(screen.getByText('Available')).toBeInTheDocument();
  });
});
```

## 📝 Code Style

### Go Code Style

Wir verwenden folgende Standards und Tools:

- **gofmt**: Code-Formatierung
- **golint**: Linting
- **go vet**: Static Analysis
- **gosec**: Security Scanning
- **staticcheck**: Advanced Analysis

### Beispiel

```go
// ✅ Guter Stil
package service

import (
    "context"
    "fmt"
    "time"

    "github.com/google/uuid"
    "github.com/scooter-share-pro/shared/pkg/errors"
    "github.com/scooter-share-pro/shared/pkg/logger"
)

// UserService handles user-related business logic.
type UserService struct {
    repo   UserRepository
    logger logger.Logger
}

// NewUserService creates a new UserService instance.
func NewUserService(repo UserRepository, logger logger.Logger) *UserService {
    return &UserService{
        repo:   repo,
        logger: logger,
    }
}

// CreateUser creates a new user with the given parameters.
func (s *UserService) CreateUser(ctx context.Context, req *CreateUserRequest) (*User, error) {
    if err := req.Validate(); err != nil {
        return nil, errors.NewValidationError("invalid request", err)
    }

    existingUser, err := s.repo.GetByEmail(ctx, req.Email)
    if err != nil && !errors.IsNotFound(err) {
        return nil, fmt.Errorf("failed to check existing user: %w", err)
    }
    if existingUser != nil {
        return nil, errors.NewConflictError("user already exists")
    }

    user := &User{
        ID:        uuid.New().String(),
        Email:     req.Email,
        Name:      req.Name,
        Status:    UserStatusActive,
        CreatedAt: time.Now(),
        UpdatedAt: time.Now(),
    }

    if err := s.repo.Create(ctx, user); err != nil {
        return nil, fmt.Errorf("failed to create user: %w", err)
    }

    s.logger.Info("User created successfully", 
        logger.String("user_id", user.ID),
        logger.String("email", user.Email))

    return user, nil
}

// ❌ Schlechter Stil
func createuser(email string, name string) (User, error) {
    u := User{Email: email, Name: name}
    err := db.Create(u)
    return u, err
}
```

### React/TypeScript Code Style

```typescript
// ✅ Guter Stil
import React, { useState, useEffect, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchScooters, selectScooters, selectLoading } from '../store/slices/scooterSlice';
import { Scooter, ScooterFilters } from '../types/scooter';
import { ScooterMap } from './ScooterMap';
import { ScooterList } from './ScooterList';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';

interface ScooterDashboardProps {
  onScooterSelect?: (scooter: Scooter) => void;
  filters?: Partial<ScooterFilters>;
}

export const ScooterDashboard: React.FC<ScooterDashboardProps> = ({
  onScooterSelect,
  filters = {},
}) => {
  const dispatch = useDispatch();
  const { scooters, loading, error } = useSelector(selectScooters);
  const [selectedScooter, setSelectedScooter] = useState<Scooter | null>(null);

  const handleScooterClick = useCallback((scooter: Scooter) => {
    setSelectedScooter(scooter);
    onScooterSelect?.(scooter);
  }, [onScooterSelect]);

  useEffect(() => {
    dispatch(fetchScooters(filters));
  }, [dispatch, filters]);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  return (
    <div className="scooter-dashboard">
      <div className="dashboard-content">
        <ScooterMap
          scooters={scooters}
          selectedScooter={selectedScooter}
          onScooterClick={handleScooterClick}
        />
        <ScooterList
          scooters={scooters}
          selectedScooter={selectedScooter}
          onScooterClick={handleScooterClick}
        />
      </div>
    </div>
  );
};

// ❌ Schlechter Stil
function ScooterDashboard(props) {
  const [scooters, setScooters] = useState([]);
  
  useEffect(() => {
    fetch('/api/scooters')
      .then(res => res.json())
      .then(data => setScooters(data));
  }, []);
  
  return (
    <div>
      {scooters.map(scooter => (
        <div key={scooter.id}>{scooter.name}</div>
      ))}
    </div>
  );
}
```

## 🐛 Bug Reports

### Bug Report Guidelines

1. **Reproduzierbarkeit** ist entscheidend
2. **Environment Details** immer angeben
3. **Logs und Screenshots** anhängen
4. **Minimal Example** wenn möglich

### Bug Report Template

```markdown
## Bug Description
Klare, präzise Beschreibung des Bugs

## Severity
- [ ] Critical (System down)
- [ ] High (Major feature broken)
- [ ] Medium (Minor feature broken)
- [ ] Low (Cosmetic issue)

## Environment
- Kubernetes Version: [z.B. 1.28.2]
- Docker Version: [z.B. 24.0.0]
- Go Version: [z.B. 1.21.5]
- Browser: [z.B. Chrome 120]
- Deployment: [Local/Dev/Staging/Prod]

## Steps to Reproduce
1. `kubectl apply -f k8s/services/user-service.yaml`
2. `curl -X POST http://localhost:8080/api/v1/users`
3. Input: `{"email": "invalid-email"}`
4. Siehe 500 Internal Server Error

## Expected Behavior
- [ ] Should return 400 Bad Request
- [ ] Should return validation error details
- [ ] Should not crash the service

## Actual Behavior
- [ ] Returns 500 Internal Server Error
- [ ] Service crashes and restarts
- [ ] No meaningful error message

## Logs
```
2024-01-15T10:30:00Z ERROR user-service: panic: runtime error:
goroutine 123 [running]:
main.createUserHandler(...)
```

## Additional Context
- Happens only in production
- Started after recent deployment
- Affects 10% of user creation requests
```

## ✨ Feature Requests

### Feature Request Process

1. **Idea Discussion** im GitHub Discussions
2. **Technical Specification** erstellen
3. **Design Review** mit Architecture Team
4. **Implementation Planning** mit Product Owner

### Feature Request Template

```markdown
## Feature Description
Detaillierte Beschreibung des gewünschten Features

## Business Value
- Revenue Impact: [z.B. +15% user retention]
- Cost Savings: [z.B. -20% support tickets]
- Competitive Advantage: [z.B. First in market]

## Technical Requirements
### API Changes
- New endpoints: `POST /api/v1/scooters/{id}/reserve`
- Database changes: Add reservation table
- Authentication: Required

### Frontend Changes
- New components: ReservationModal
- Routes: /scooters/:id/reserve
- State management: Reservation slice

### Infrastructure Changes
- New service: Reservation Service
- Database migrations: 001_add_reservations.sql
- Monitoring: New metrics and alerts

## Acceptance Criteria
- [ ] User can reserve scooter for 15 minutes
- [ ] Reservation expires automatically
- [ ] User gets notification before expiry
- [ ] System handles 1000+ concurrent reservations
- [ ] Performance: < 100ms response time

## Dependencies
- Payment Service integration
- Notification Service updates
- Database schema changes

## Timeline Estimate
- Design: 1 week
- Development: 2 weeks
- Testing: 1 week
- Deployment: 2 days

## Risks and Mitigations
- Risk: Database performance under load
- Mitigation: Implement caching layer
- Risk: Race conditions in reservations
- Mitigation: Use distributed locks
```

## 🔄 Pull Request Guidelines

### PR Process

1. **Create Draft PR** für frühes Feedback
2. **Self-Review** mit Checklist
3. **Automated Checks** bestehen
4. **Code Review** von mindestens 2 Teammitgliedern
5. **Integration Tests** in Staging
6. **Merge** nach main

### PR Checklist

#### Code Quality
- [ ] Code follows project style guidelines
- [ ] All tests pass (>90% coverage)
- [ ] No security vulnerabilities
- [ ] Performance impact assessed

#### Documentation
- [ ] API documentation updated
- [ ] README.md updated if needed
- [ ] CHANGELOG.md updated
- [ ] Architecture diagrams updated

#### Testing
- [ ] Unit tests written
- [ ] Integration tests added
- [ ] E2E tests updated
- [ ] Manual testing completed

#### Deployment
- [ ] Kubernetes manifests updated
- [ ] Helm charts updated
- [ ] Migration scripts tested
- [ ] Rollback plan documented

### PR Template

```markdown
## Description
Kurze Beschreibung der Änderungen und warum sie notwendig sind

## Type of Change
- [ ] Bugfix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Infrastructure change

## Testing
- [ ] Unit tests: `make test-go` and `make test-frontend`
- [ ] Integration tests: `make integration-test`
- [ ] E2E tests: `make e2e-test`
- [ ] Manual testing in staging environment

## Performance Impact
- [ ] No performance impact
- [ ] Improved performance: [details]
- [ ] Performance degradation: [details and mitigation]

## Security Considerations
- [ ] No security changes
- [ ] Security improvements: [details]
- [ ] Security risks identified: [details and mitigation]

## Breaking Changes
- [ ] No breaking changes
- [ ] API changes: [details]
- [ ] Database changes: [details]
- [ ] Configuration changes: [details]

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published
```

## 📚 Documentation

### Documentation Types

1. **API Documentation**: OpenAPI 3.0 Specs
2. **Architecture Documentation**: C4 Models, ADRs
3. **User Documentation**: Admin Guides, Tutorials
4. **Developer Documentation**: Setup, Debugging

### API Documentation Example

```yaml
# api/user-service/v1/openapi.yaml
openapi: 3.0.3
info:
  title: User Service API
  version: 1.0.0
  description: User management and authentication

paths:
  /api/v1/users:
    post:
      summary: Create a new user
      description: Creates a new user with email and password
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
      responses:
        '201':
          description: User created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          $ref: '#/components/responses/BadRequest'
        '409':
          $ref: '#/components/responses/Conflict'

components:
  schemas:
    CreateUserRequest:
      type: object
      required:
        - email
        - password
        - name
      properties:
        email:
          type: string
          format: email
          example: user@example.com
        password:
          type: string
          minLength: 8
          example: securepassword123
        name:
          type: string
          minLength: 2
          maxLength: 100
          example: John Doe
```

### Architecture Decision Records (ADRs)

```markdown
# ADR-001: Use Microservices Architecture

## Status
Accepted

## Context
We need to build a scalable E-Scooter sharing platform that can handle:
- 100,000+ concurrent users
- Multiple geographic regions
- Independent deployment of features
- Different scaling requirements per service

## Decision
We will use a microservices architecture with the following services:
- User Service (authentication, profiles)
- Scooter Service (fleet management)
- Rental Service (booking, pricing)
- Payment Service (transactions, billing)
- Notification Service (emails, SMS, push)

## Consequences
### Positive
- Independent scaling and deployment
- Technology diversity per service
- Better fault isolation
- Team autonomy

### Negative
- Increased operational complexity
- Network latency between services
- Data consistency challenges
- Higher infrastructure costs

## Mitigations
- Service mesh (Istio) for communication
- Event-driven architecture for consistency
- Comprehensive monitoring and observability
- Automated deployment and testing
```

## 🚀 Deployment

### Development Deployment

```bash
# Local Development
make dev-up

# Kubernetes Development
kubectl apply -f k8s/development/
make port-forward

# Docker Compose
docker-compose -f docker-compose.dev.yml up -d
```

### Staging Deployment

```bash
# Deploy to Staging
make deploy-staging

# Run Integration Tests
make integration-test-staging

# Performance Testing
make load-test-staging
```

### Production Deployment

```bash
# Deploy to Production
make deploy-production

# Health Checks
make health-check

# Rollback if needed
make rollback-production
```

### Environment Configuration

```yaml
# environments/production/values.yaml
global:
  environment: production
  domain: scooter-share-pro.com

services:
  user-service:
    replicas: 3
    resources:
      requests:
        cpu: 250m
        memory: 512Mi
      limits:
        cpu: 500m
        memory: 1Gi
    env:
      DATABASE_URL: "postgresql://user:pass@postgres:5432/users"
      REDIS_URL: "redis://redis:6379"

  scooter-service:
    replicas: 5
    resources:
      requests:
        cpu: 500m
        memory: 1Gi
      limits:
        cpu: 1000m
        memory: 2Gi

monitoring:
  prometheus:
    enabled: true
  grafana:
    enabled: true
  jaeger:
    enabled: true
```

## 🧪 Testing Strategy

### Test Pyramid Implementation

```bash
# Unit Tests (70% - Fast, Isolated)
make test-unit
# Coverage target: >90%

# Integration Tests (20% - Service Interactions)
make test-integration
# Coverage target: >80%

# E2E Tests (10% - Full Workflows)
make test-e2e
# Coverage target: Critical paths only
```

### Test Data Management

```go
// tests/fixtures/user_fixtures.go
package fixtures

import (
    "context"
    "testing"
    
    "github.com/scooter-share-pro/user-service/internal/model"
    "github.com/stretchr/testify/require"
)

type UserFixtures struct {
    AdminUser     *model.User
    CustomerUser  *model.User
    ProviderUser  *model.User
}

func CreateUserFixtures(t *testing.T, ctx context.Context, repo UserRepository) *UserFixtures {
    admin := &model.User{
        ID:    "admin-123",
        Email: "admin@test.com",
        Name:  "Admin User",
        Role:  model.RoleAdmin,
        Status: model.StatusActive,
    }
    
    customer := &model.User{
        ID:    "customer-123",
        Email: "customer@test.com",
        Name:  "Customer User",
        Role:  model.RoleCustomer,
        Status: model.StatusActive,
    }
    
    provider := &model.User{
        ID:    "provider-123",
        Email: "provider@test.com",
        Name:  "Provider User",
        Role:  model.RoleProvider,
        Status: model.StatusActive,
    }
    
    require.NoError(t, repo.Create(ctx, admin))
    require.NoError(t, repo.Create(ctx, customer))
    require.NoError(t, repo.Create(ctx, provider))
    
    return &UserFixtures{
        AdminUser:    admin,
        CustomerUser: customer,
        ProviderUser: provider,
    }
}
```

## 🤝 Community Guidelines

### Code of Conduct

1. **Respect**: Treat everyone with respect and professionalism
2. **Inclusivity**: Welcome contributors from all backgrounds
3. **Constructiveness**: Provide helpful, constructive feedback
4. **Collaboration**: Work together to achieve common goals

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Slack**: Real-time collaboration (invite-only)
- **Email**: Private matters and security issues

### Recognition Program

- **Contributor of the Month**: Recognized in company newsletter
- **Top Contributors**: Featured in README.md
- **Innovation Awards**: For breakthrough contributions
- **Mentorship Program**: Senior contributors mentor newcomers

## 📞 Getting Help

### Self-Service Resources

1. **Documentation**: Comprehensive guides in `/docs`
2. **API Reference**: OpenAPI specs for all services
3. **Architecture Diagrams**: C4 models in `/docs/architecture`
4. **Troubleshooting**: Common issues and solutions

### Community Support

1. **GitHub Discussions**: Ask questions and share ideas
2. **Issue Templates**: Use provided templates for bugs/features
3. **Wiki**: Community-maintained knowledge base
4. **Office Hours**: Weekly video calls with maintainers

### Direct Support

For urgent issues or security concerns:
- **Email**: security@scooter-share-pro.com
- **Slack**: #support channel
- **Phone**: +49-123-456789 (emergency only)

## 🏆 Recognition

### Contribution Types

1. **Code Contributions**: Pull requests with code changes
2. **Documentation**: Improving docs, tutorials, examples
3. **Bug Reports**: High-quality issue reports
4. **Community Support**: Helping others in discussions
5. **Testing**: Writing and maintaining test suites
6. **Infrastructure**: DevOps and deployment improvements

### Contributor Levels

- **Contributor**: 1+ merged pull requests
- **Active Contributor**: 5+ merged pull requests
- **Core Contributor**: 20+ merged pull requests
- **Maintainer**: Trusted team member with merge access

---

## 📄 Licensing

By contributing to Scooter-Share-Pro, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to Scooter-Share-Pro!** 🎉

Your contributions help us build the world's most advanced E-Scooter sharing platform.
