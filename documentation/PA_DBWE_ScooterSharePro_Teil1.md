# Praxisarbeit DBWE.TA1A.PA

## Datenbanken und Webentwicklung

### ScooterShare Pro – Enterprise E-Scooter Rental Platform

---

**Verfasser:**  
Luca Brunner  
Bundesgasse 42, 3011 Bern  
luca.brunner@student.ipso.ch

**Studiengang:** HFINFP.A.BA.5.25-BE-S2504

**Bildungsinstitution:** IPSO – Höhere Fachschule der digitalen Wirtschaft

**Eingabedatum:** 20. März 2026

---

## Inhaltsverzeichnis

1. Management Summary
2. Anwendung
   - 2.1 Anforderungskatalog
   - 2.2 Benutzerhandbuch
   - 2.3 API-Schnittstelle
3. Softwarearchitektur
   - 3.1 Datenmodell (ERD)
   - 3.2 Systemübersicht
   - 3.3 Prozessabläufe
   - 3.4 Deployment
4. Qualitätssicherung
5. Schlussfolgerungen
6. Literaturverzeichnis
7. Appendix

---

## 1 Management Summary

Im Rahmen dieser Praxisarbeit wurde **ScooterShare Pro** entwickelt, eine professionelle Webplattform für den Verleih von E-Scootern. Die Applikation adressiert die Anforderungen moderner urbaner Mobilität und bietet sowohl Endanwendern als auch Flottenanbietern eine umfassende Lösung.

### Projektkontext

Das Projekt basiert auf der Normaufgabe des DBWE-Moduls: Eine Stadtverwaltung beauftragt die Entwicklung einer Online-Plattform, über welche E-Scooter von verschiedenen Anbietern verwaltet und von Nutzern gemietet werden können.

### Technische Umsetzung

Die Implementierung erfolgte mit bewährten Technologien:

| Komponente | Technologie |
|------------|-------------|
| Backend | Python 3.11, Flask 2.3 |
| Datenbank | PostgreSQL |
| Deployment | Render.com (PaaS) |
| Webserver | Gunicorn |

Die produktive Instanz ist unter **https://scooter-share-pro.onrender.com/** verfügbar.

### Kernfunktionalitäten

- Dreistufiges Rollenkonzept (Kunde, Anbieter, Administrator)
- Vollständige Scooter-Flottenverwaltung mit GPS-Tracking
- Automatisierte Preisberechnung (Grundgebühr + Minutentarif)
- RESTful API mit JWT-Authentifizierung und Swagger-Dokumentation

### Bewertung

**Stärken:** Modulare Architektur, saubere API-Trennung, umfassende Dokumentation

**Risiken:** Abhängigkeit von Render-Plattform, Free-Tier-Einschränkungen

**Empfehlung:** Für den Produktiveinsatz wird eine Migration auf dedizierte Infrastruktur empfohlen.

---

## 2 Anwendung

### 2.1 Anforderungskatalog

Die nachfolgende Tabelle dokumentiert die Umsetzung der funktionalen Anforderungen gemäss Normaufgabe.

#### Funktionale Anforderungen

| ID | Beschreibung | Implementierung |
|----|--------------|-----------------|
| REQ-01 | Anbieter-Registrierung | ✓ Vollständig |
| REQ-02 | Fahrer-Registrierung | ✓ Vollständig |
| REQ-03 | Scooter-CRUD-Operationen | ✓ Vollständig |
| REQ-04 | Scooter-Attribute (ID, Akku, GPS) | ✓ Vollständig |
| REQ-05 | QR-Code-Funktionalität | ✓ Vollständig |
| REQ-06 | Zeit- und Streckenerfassung | ✓ Vollständig |
| REQ-07 | Minutengenaue Abrechnung | ✓ Vollständig |
| REQ-08 | Zahlungsabwicklung | ✓ Vollständig |

#### Nicht-funktionale Anforderungen

| ID | Beschreibung | Status |
|----|--------------|--------|
| NFR-01 | Erweiterbarkeit (E-Bikes) | Architektur vorbereitet |
| NFR-02 | 500 parallele Ausleihen | Theoretisch unterstützt |

#### Technische Vorgaben

| Vorgabe | Realisierung |
|---------|--------------|
| Relationales DBMS | PostgreSQL (Render Managed) |
| Python ≥ 3.9 | Python 3.11 |
| Flask Framework | Flask 2.3 + Extensions |
| Gunicorn Webserver | Gunicorn 21.2.0 |
