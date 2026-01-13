### 3.3 Prozessabläufe

#### Sequenzdiagramm: Ausleihvorgang

```
Kunde      Browser      Controller     Service       Database
  │           │             │             │             │
  │──Scooter──▶             │             │             │
  │  wählen   │             │             │             │
  │           │──GET────────▶             │             │
  │           │             │──findById()─▶             │
  │           │             │             │──SELECT─────▶
  │           │             │             │◀──Scooter───│
  │           │◀──HTML──────│             │             │
  │◀──Seite───│             │             │             │
  │           │             │             │             │
  │──"Rent"───▶             │             │             │
  │           │──POST───────▶             │             │
  │           │             │──startRental()──▶        │
  │           │             │             │──validate()─▶
  │           │             │             │◀──OK────────│
  │           │             │             │──INSERT─────▶
  │           │             │             │──UPDATE─────▶
  │           │◀──redirect──│             │             │
  │◀──Dashboard│             │             │             │
```

#### Aktivitätsdiagramm: Preiskalkulation

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Endzeit     │
│ erfassen    │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Dauer berechnen     │
│ (Ende - Start)      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Preisformel:        │
│                     │
│ Total = Grundgebühr │
│ + (Minuten × Tarif) │
│                     │
│ Beispiel:           │
│ 1.00 + (15 × 0.25)  │
│ = CHF 4.75          │
└──────┬──────────────┘
       │
       ▼
┌─────────────┐
│ Speichern   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    ENDE     │
└─────────────┘
```

#### Zustandsautomat: Scooter-Lifecycle

```
                    ┌──────────┐
        ┌───────────│ CREATED  │
        │           └────┬─────┘
        │                │ activate()
        │                ▼
        │           ┌──────────┐
        │    ┌──────│AVAILABLE │◀─────────┐
        │    │      └────┬─────┘          │
        │    │           │ rent()         │ return()
        │    │           ▼                │
        │    │      ┌──────────┐          │
        │    │      │  IN_USE  │──────────┘
        │    │      └────┬─────┘
        │    │           │ reportIssue()
        │    │           ▼
        │    │      ┌──────────┐
        │    └─────▶│MAINTENANCE│
        │           └────┬─────┘
        │                │ repair()
        │                ▼
        │           ┌──────────┐
        └──────────▶│ OFFLINE  │
                    └──────────┘
```

### 3.4 Deployment

Die Produktivumgebung wird auf **Render.com** (Platform as a Service) betrieben.

#### Infrastrukturdiagramm

```
┌─────────────────────────────────────────────┐
│                 INTERNET                    │
│    ┌──────────┐        ┌──────────┐        │
│    │ Browser  │        │ Postman  │        │
│    └────┬─────┘        └────┬─────┘        │
└─────────┼───────────────────┼───────────────┘
          └─────────┬─────────┘
                    │ HTTPS
                    ▼
┌─────────────────────────────────────────────┐
│            RENDER.COM PLATFORM              │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │           Web Service                 │ │
│  │                                       │ │
│  │  ┌─────────────┐  ┌─────────────┐    │ │
│  │  │  Gunicorn   │  │  Flask App  │    │ │
│  │  │  4 Workers  │─▶│             │    │ │
│  │  │  Port $PORT │  │  - Web      │    │ │
│  │  └─────────────┘  │  - API      │    │ │
│  │                   │  - Swagger  │    │ │
│  │                   └─────────────┘    │ │
│  └───────────────────────────────────────┘ │
│                    │                        │
│                    ▼ Internal Network       │
│  ┌───────────────────────────────────────┐ │
│  │        PostgreSQL Database            │ │
│  │                                       │ │
│  │  Tables: users, scooters, rentals,   │ │
│  │          payments, ratings            │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Environment:                               │
│  - FLASK_ENV=production                    │
│  - DATABASE_URL=postgresql://...           │
│  - SECRET_KEY=***                          │
│  - JWT_SECRET_KEY=***                      │
│  - BASE_PRICE_PER_MINUTE=0.25             │
│  - START_FEE=1.00                          │
└─────────────────────────────────────────────┘

URL: https://scooter-share-pro.onrender.com/
API Docs: https://scooter-share-pro.onrender.com/api/docs/
GitHub: https://github.com/eazybusiness/scooter-share-pro
```

#### Technologieentscheidungen

| Aspekt | Wahl | Begründung |
|--------|------|------------|
| Hosting | Render.com | Git-Integration, Managed PostgreSQL, Free Tier |
| WSGI | Gunicorn | Produktionsreif, Multi-Processing |
| Datenbank | PostgreSQL | ACID-Compliance, JSON-Support, Geo-Daten |
| Framework | Flask | Modular, Unterrichtsbezug |
| ORM | SQLAlchemy | Query-Abstraktion, Migrations |
| Auth | JWT | Stateless, Skalierbar |
| Docs | Flask-RESTX | Swagger UI integriert |

#### Abweichungen vom Unterrichtsstoff

| Erweiterung | Motivation |
|-------------|------------|
| Render statt lokal | Anforderung: Internetverfügbarkeit |
| Repository Pattern | Bessere Testbarkeit |
| Swagger/OpenAPI | Professionelle API-Dokumentation |
| PostgreSQL statt MySQL | Native Render-Unterstützung |
