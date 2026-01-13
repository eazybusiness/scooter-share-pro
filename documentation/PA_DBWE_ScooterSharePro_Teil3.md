## 3 Softwarearchitektur

### 3.1 Datenmodell (ERD)

Das relationale Datenbankschema wurde gemäss der dritten Normalform konzipiert.

#### Entity-Relationship-Diagramm

```
┌─────────────────┐         ┌─────────────────┐
│     users       │         │    scooters     │
├─────────────────┤         ├─────────────────┤
│ PK id           │         │ PK id           │
│    email (UQ)   │         │    identifier   │
│    password_hash│         │    qr_code (UQ) │
│    first_name   │         │    model        │
│    last_name    │         │    brand        │
│    role         │◀────┐   │    latitude     │
│    phone        │     │   │    longitude    │
│    is_active    │     │   │    status       │
│    created_at   │     │   │    battery      │
└────────┬────────┘     │   │ FK provider_id ─┼───┘
         │              │   │    price_min    │
         │              │   │    created_at   │
         │              │   └────────┬────────┘
         │              │            │
         │   ┌──────────┴────────────┘
         │   │
         ▼   ▼
┌─────────────────────┐
│      rentals        │
├─────────────────────┤
│ PK id               │
│    rental_code (UQ) │
│ FK user_id          │
│ FK scooter_id       │
│    start_time       │
│    end_time         │
│    start_latitude   │
│    start_longitude  │
│    end_latitude     │
│    end_longitude    │
│    duration_min     │
│    distance_km      │
│    total_cost       │
│    status           │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
┌──────────┐ ┌──────────┐
│ payments │ │ ratings  │
├──────────┤ ├──────────┤
│ PK id    │ │ PK id    │
│ FK rental│ │ FK rental│
│   amount │ │   score  │
│   method │ │   comment│
│   status │ │ created  │
│   trans_id│ └──────────┘
└──────────┘
```

#### Entitätsbeschreibungen

**users** – Benutzerstammdaten
- Rollenattribut: 'customer', 'provider', 'admin'
- Passwort: bcrypt-Hash mit Salt
- Soft-Delete via is_active Flag

**scooters** – Fahrzeugregister
- identifier: Menschenlesbare Kennung (z.B. SSP-001)
- qr_code: Maschinenlesbarer Unique Identifier
- status: 'available', 'in_use', 'maintenance', 'offline'
- provider_id: Referenz zum Flottenbesitzer

**rentals** – Ausleihprotokoll
- Zeitstempel für Start und Ende
- GPS-Koordinaten beider Positionen
- Berechnete Felder: duration_min, total_cost

**payments** – Transaktionslog
- method: 'credit_card', 'paypal', 'twint', 'invoice'
- status: 'pending', 'completed', 'failed', 'refunded'

**ratings** – Bewertungssystem
- score: Integer 1-5
- Optional: Freitextkommentar

### 3.2 Systemübersicht

Die Applikation implementiert eine Schichtenarchitektur nach dem MVC-Paradigma.

#### Architekturdiagramm

```
┌───────────────────────────────────────────┐
│           PRÄSENTATIONSSCHICHT            │
│                                           │
│  ┌─────────────┐    ┌─────────────┐      │
│  │   Browser   │    │  API Client │      │
│  │  Bootstrap  │    │   Swagger   │      │
│  │   Jinja2    │    │    JSON     │      │
│  └─────────────┘    └─────────────┘      │
└───────────────────────────────────────────┘
                    │
                    ▼ HTTP/HTTPS
┌───────────────────────────────────────────┐
│           ANWENDUNGSSCHICHT               │
│                                           │
│  ┌───────────────────────────────────┐   │
│  │         Flask Application         │   │
│  │                                   │   │
│  │  ┌──────────┐   ┌──────────┐     │   │
│  │  │   Web    │   │   API    │     │   │
│  │  │ Routes   │   │ Routes   │     │   │
│  │  └──────────┘   └──────────┘     │   │
│  │                                   │   │
│  │  ┌───────────────────────────┐   │   │
│  │  │     Service Layer         │   │   │
│  │  │  - RentalService          │   │   │
│  │  │  - PaymentService         │   │   │
│  │  │  - ScooterService         │   │   │
│  │  └───────────────────────────┘   │   │
│  │                                   │   │
│  │  ┌───────────────────────────┐   │   │
│  │  │    Repository Layer       │   │   │
│  │  │  - UserRepository         │   │   │
│  │  │  - ScooterRepository      │   │   │
│  │  └───────────────────────────┘   │   │
│  └───────────────────────────────────┘   │
└───────────────────────────────────────────┘
                    │
                    ▼ SQLAlchemy ORM
┌───────────────────────────────────────────┐
│            DATENSCHICHT                   │
│                                           │
│  ┌───────────────────────────────────┐   │
│  │        PostgreSQL Database        │   │
│  │         (Render Managed)          │   │
│  └───────────────────────────────────┘   │
└───────────────────────────────────────────┘
```

#### Verzeichnisstruktur

```
scooter-share-pro/
├── app/
│   ├── __init__.py        # Application Factory
│   ├── models/            # SQLAlchemy Models
│   ├── repositories/      # Data Access Layer
│   ├── services/          # Business Logic
│   ├── api/               # REST Endpoints
│   ├── web/               # Web Routes
│   ├── templates/         # Jinja2 Templates
│   └── static/            # Assets
├── config.py              # Configuration
├── requirements.txt       # Dependencies
└── run.py                 # Entry Point
```
