### 2.2 Benutzerhandbuch

#### Rollenbasiertes Zugriffskonzept

Die Applikation implementiert ein dreistufiges Berechtigungsmodell:

**Customer (Endkunde)**
- Kontoerstellung und Profilverwaltung
- Scooter-Suche nach Verfügbarkeit und Standort
- Ausleihe initiieren und beenden
- Zahlungshistorie einsehen

**Provider (Flottenanbieter)**
- Sämtliche Customer-Funktionen
- Eigene Scooter-Flotte verwalten (CRUD)
- Umsatz- und Nutzungsstatistiken
- Wartungsstatus pflegen

**Admin (Systemadministrator)**
- Globale Benutzer- und Scooterverwaltung
- Systemweite Konfiguration
- Reporting und Analytics

#### Anwendungsszenarien

**Szenario 1: Erstregistrierung**
1. Webseite aufrufen: https://scooter-share-pro.onrender.com/
2. Navigation zu «Register»
3. Eingabe: E-Mail, Passwort, Personalien
4. Rollenwahl: Customer oder Provider
5. Bestätigung und automatischer Login

**Szenario 2: Scooter-Ausleihe**
1. Authentifizierung im System
2. Menüpunkt «Available Scooters»
3. Kartenansicht oder Listenfilter nutzen
4. Scooter-Details prüfen (Akku, Preis, Distanz)
5. «Rent Now» aktivieren
6. GPS-Position freigeben
7. Fahrt beginnt – Timer läuft

**Szenario 3: Rückgabe und Abrechnung**
1. Dashboard öffnen
2. Aktive Ausleihe anzeigen
3. «End Rental» auswählen
4. Endposition wird erfasst
5. Automatische Kostenberechnung
6. Rechnung wird generiert

#### Testzugänge für Prüfung

| Funktion | Benutzername | Kennwort |
|----------|--------------|----------|
| Administrator | admin@scootershare.com | Admin123! |
| Flottenanbieter | provider@scootershare.com | Provider123! |
| Endkunde | kunde@scootershare.com | Kunde123! |

### 2.3 API-Schnittstelle

Die REST-API folgt den OpenAPI-Spezifikationen und ist unter `/api/docs/` interaktiv dokumentiert.

**Basis-Endpunkt:** https://scooter-share-pro.onrender.com/api

#### Authentifizierungsmechanismus

Die API verwendet JSON Web Tokens (JWT) für die Zugriffskontrolle.

**Token-Beschaffung:**
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "admin@scootershare.com",
  "password": "Admin123!"
}
```

**Antwortstruktur:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "admin@scootershare.com",
    "role": "admin"
  }
}
```

**Header-Integration:**
```
Authorization: Bearer <access_token>
```

#### Ressourcen-Endpunkte

**Scooter-Management:**

| HTTP | Endpunkt | Funktion | Berechtigung |
|------|----------|----------|--------------|
| GET | /api/scooters | Listenabfrage | Authentifiziert |
| GET | /api/scooters/available | Verfügbare Einheiten | Authentifiziert |
| GET | /api/scooters/{id} | Einzelabfrage | Authentifiziert |
| POST | /api/scooters | Neuanlage | Provider/Admin |
| PUT | /api/scooters/{id} | Aktualisierung | Provider/Admin |
| DELETE | /api/scooters/{id} | Löschung | Provider/Admin |

**Rental-Operations:**

| HTTP | Endpunkt | Funktion | Berechtigung |
|------|----------|----------|--------------|
| GET | /api/rentals | Eigene Ausleihen | Authentifiziert |
| POST | /api/rentals | Neue Ausleihe | Customer |
| GET | /api/rentals/{id} | Detailansicht | Eigentümer |
| POST | /api/rentals/{id}/end | Beendigung | Eigentümer |
| POST | /api/rentals/{id}/rating | Bewertung | Eigentümer |

**Beispielaufruf – Verfügbare Scooter:**
```bash
curl -X GET "https://scooter-share-pro.onrender.com/api/scooters/available" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Accept: application/json"
```
