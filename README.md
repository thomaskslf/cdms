# CDMS — Kundendokumenten-Verwaltungssystem

Lokales Web-Tool zur Verwaltung technischer Kundendokumente mit Versionsverfolgung und automatischem Dokumentenvergleich.

## Schnellstart

```
start.bat
```

Dann: http://localhost:5173

Beim ersten Start: Admin-Account anlegen über:
```
POST http://localhost:8000/api/auth/setup
{ "username": "admin", "email": "admin@firma.de", "password": "sicher123" }
```
Oder im Browser: http://localhost:8000/docs → `/api/auth/setup`

## Unterstützte Formate
- PDF, Excel (.xlsx, .xls), CSV
- CAD-Zeichnungen (DXF, DWG*)
- Bilder (JPG, PNG, TIFF) — mit OCR-Texterkennung*

*DWG: Nur Metadaten, kein Entity-Parsing
*OCR: Erfordert Tesseract-Installation (optional)

## Features
- **Auto-Klassifizierung** nach Dokumenttyp (Zeichnung, Stückliste, Montage, etc.)
- **Ordner-Upload**: ganzen Ordner per Drag & Drop oder lokalen Pfad scannen
- **Versionsverlauf**: wer hat wann welche Version eingepflegt
- **Automatischer Vergleich** beim Upload — zeigt was sich geändert hat
- **Stücklisten-Diff**: tabellarisch, welche Teile neu/entfernt/geändert
- **Text-Diff**: Zeilen-Diff für PDFs und Anweisungen
- **DXF-Diff**: Entity-Counts und Layer-Änderungen

## Entwicklung

```bash
# Backend
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev
```
