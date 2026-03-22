"""
Demo seed script — creates sample customers, projects, documents and versions.
Runs on every container start but skips if data already exists (idempotent).
"""
import os
import sys
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# ── Bootstrap ─────────────────────────────────────────────────────────────────
os.chdir(Path(__file__).parent)
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.customer import Customer
from app.models.project import Project
from app.models.document import Document, DocType, DocumentStatus
from app.models.document_version import DocumentVersion
from app.models.activity_log import ActivityLog
from app.services.auth_service import get_password_hash
from app.config import settings

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ── Skip if already seeded ────────────────────────────────────────────────────
if db.query(User).count() > 0:
    print("Seed: database already populated, skipping.")
    db.close()
    sys.exit(0)

print("Seed: creating demo data...")

storage_root = Path(settings.storage_root)
storage_root.mkdir(parents=True, exist_ok=True)

# ── Users ─────────────────────────────────────────────────────────────────────
admin = User(username="admin", email="admin@demo.de", password_hash=get_password_hash("demo1234"), is_admin=True)
hans = User(username="h.mueller", email="h.mueller@firma.de", password_hash=get_password_hash("demo1234"))
lisa = User(username="l.schmidt", email="l.schmidt@firma.de", password_hash=get_password_hash("demo1234"))
db.add_all([admin, hans, lisa])
db.flush()

# ── Customers ─────────────────────────────────────────────────────────────────
acme = Customer(name="ACME Maschinenbau GmbH", slug="acme-maschinenbau")
techno = Customer(name="TechnoKraft AG", slug="technokraft-ag")
db.add_all([acme, techno])
db.flush()

# ── Projects ──────────────────────────────────────────────────────────────────
proj_a = Project(customer_id=acme.id, name="Förderbandanlage Typ 3", slug="foerderbandanlage-typ-3",
                 description="Automatische Förderbandanlage für Produktionslinie 3")
proj_b = Project(customer_id=acme.id, name="Steuerungsschrank SK-200", slug="steuerungsschrank-sk-200",
                 description="Schaltschrankbau für Anlage 200")
proj_c = Project(customer_id=techno.id, name="Hydraulikpresse HY-50", slug="hydraulikpresse-hy-50",
                 description="50-Tonnen Hydraulikpresse, Baujahr 2024")
db.add_all([proj_a, proj_b, proj_c])
db.flush()

# ── Helper: create a fake file + version ─────────────────────────────────────
def make_version(
    doc: Document,
    uploader: User,
    version_number: str,
    filename: str,
    mime_type: str,
    content: bytes,
    change_summary: str,
    uploaded_at: datetime,
    extracted_text: str = "",
    extracted_data: dict = None,
    is_current: bool = False,
):
    sha256 = hashlib.sha256(content).hexdigest()
    ver_dir = storage_root / f"customers/{doc.project.customer_id}/projects/{doc.project_id}/{doc.doc_type.value}/demo"
    ver_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(filename).suffix
    fpath = ver_dir / f"{sha256[:8]}{ext}"
    fpath.write_bytes(content)
    rel_path = str(fpath.relative_to(storage_root))

    v = DocumentVersion(
        document_id=doc.id,
        version_number=version_number,
        file_path=rel_path,
        file_name=filename,
        file_size=len(content),
        mime_type=mime_type,
        sha256_hash=sha256,
        uploader_id=uploader.id,
        uploaded_at=uploaded_at,
        change_summary=change_summary,
        extracted_text=extracted_text,
        extracted_data=extracted_data,
        is_current=is_current,
    )
    db.add(v)
    db.flush()
    return v


# ── Demo: Förderbandanlage ────────────────────────────────────────────────────
# 1) Stückliste – 3 versions (shows BOM diff)
stl_doc = Document(project_id=proj_a.id, doc_type=DocType.stückliste,
                   name="Hauptstückliste Förderband", status=DocumentStatus.current)
db.add(stl_doc)
db.flush()

bom_v1_rows = [
    ["10", "0815-001", "Antriebsmotor 0,75 kW", "1", "Stk"],
    ["20", "0815-002", "Förderband 2m", "1", "Stk"],
    ["30", "0815-003", "Umlenkrolle Ø120", "2", "Stk"],
    ["40", "0815-004", "Lagerblock SN512", "4", "Stk"],
    ["50", "0815-005", "Keilriemen SPZ-1000", "2", "Stk"],
    ["60", "0815-006", "Spannschraube M12x60", "8", "Stk"],
]
bom_v2_rows = [
    ["10", "0815-001", "Antriebsmotor 1,1 kW",  "1", "Stk"],   # geändert: Leistung erhöht
    ["20", "0815-002", "Förderband 2m",          "1", "Stk"],
    ["30", "0815-003", "Umlenkrolle Ø120",       "2", "Stk"],
    ["40", "0815-004", "Lagerblock SN512",       "4", "Stk"],
    ["50", "0815-005", "Keilriemen SPZ-1000",    "3", "Stk"],   # geändert: Menge 2→3
    ["60", "0815-006", "Spannschraube M12x60",   "8", "Stk"],
    ["70", "0815-007", "Frequenzumrichter 1,5kW","1", "Stk"],   # neu
]
bom_v3_rows = [
    ["10", "0815-001", "Antriebsmotor 1,1 kW",  "1", "Stk"],
    ["20", "0815-002", "Förderband 2,5m",        "1", "Stk"],   # geändert: Länge
    ["30", "0815-003", "Umlenkrolle Ø150",       "2", "Stk"],   # geändert: Durchmesser
    ["40", "0815-004", "Lagerblock SN512",       "4", "Stk"],
    ["50", "0815-005", "Keilriemen SPZ-1250",    "3", "Stk"],   # geändert: Länge
    ["60", "0815-006", "Spannschraube M12x60",   "8", "Stk"],
    ["70", "0815-007", "Frequenzumrichter 1,5kW","1", "Stk"],
    ["80", "0815-008", "Schutzgitter 2500x800",  "2", "Stk"],   # neu
]

def bom_to_csv(rows) -> bytes:
    header = "POS,Sachnummer,Bezeichnung,Menge,Einheit\n"
    lines = "\n".join(",".join(r) for r in rows)
    return (header + lines).encode()

def bom_extracted(rows) -> dict:
    return {
        "sheets": {
            "Sheet1": {
                "columns": ["POS", "Sachnummer", "Bezeichnung", "Menge", "Einheit"],
                "rows": rows,
            }
        }
    }

stl_v1 = make_version(stl_doc, hans, "1.0", "STL_Foerderband_v1.0.csv", "text/csv",
                      bom_to_csv(bom_v1_rows), "Erstversion",
                      datetime.utcnow() - timedelta(days=60),
                      extracted_data=bom_extracted(bom_v1_rows))
stl_v2 = make_version(stl_doc, lisa, "1.1", "STL_Foerderband_v1.1.csv", "text/csv",
                      bom_to_csv(bom_v2_rows), "Motor stärker, Frequenzumrichter hinzugefügt",
                      datetime.utcnow() - timedelta(days=30),
                      extracted_data=bom_extracted(bom_v2_rows))
stl_v3 = make_version(stl_doc, hans, "1.2", "STL_Foerderband_v1.2.csv", "text/csv",
                      bom_to_csv(bom_v3_rows), "Bandlänge auf 2,5m erweitert, Schutzgitter neu",
                      datetime.utcnow() - timedelta(days=2),
                      extracted_data=bom_extracted(bom_v3_rows),
                      is_current=True)
stl_doc.current_version_id = stl_v3.id
db.flush()

# 2) Zeichnung
zng_doc = Document(project_id=proj_a.id, doc_type=DocType.zeichnung,
                   name="Gesamtzeichnung Förderband", status=DocumentStatus.current)
db.add(zng_doc)
db.flush()

zng_text_v1 = "ZEICHNUNG: Gesamtansicht Förderbandanlage Typ 3\nMassstab 1:10\nToleranz ±0,5mm\nDIN ISO 2768-m\nErstellt: 2024-01 / H.Müller"
zng_text_v2 = "ZEICHNUNG: Gesamtansicht Förderbandanlage Typ 3\nMassstab 1:10\nToleranz ±0,2mm\nDIN ISO 2768-f\nBandlänge: 2500mm (geändert von 2000mm)\nErstellt: 2024-01 / H.Müller\nGeändert: 2024-03 / L.Schmidt"

zng_v1 = make_version(zng_doc, hans, "1.0", "ZNG_Foerderband_v1.pdf", "application/pdf",
                      b"%PDF-1.4 mock content v1 drawing data",
                      "Erstzeichnung", datetime.utcnow() - timedelta(days=55),
                      extracted_text=zng_text_v1)
zng_v2 = make_version(zng_doc, lisa, "1.1", "ZNG_Foerderband_v1.1.pdf", "application/pdf",
                      b"%PDF-1.4 mock content v1.1 updated drawing tolerance changed",
                      "Toleranz verschärft, Bandlänge aktualisiert",
                      datetime.utcnow() - timedelta(days=5),
                      extracted_text=zng_text_v2, is_current=True)
zng_doc.current_version_id = zng_v2.id
db.flush()

# 3) Montagezeichnung
mnt_doc = Document(project_id=proj_a.id, doc_type=DocType.montagezeichnung,
                   name="Montagezeichnung Antriebseinheit", status=DocumentStatus.current)
db.add(mnt_doc)
db.flush()
mnt_v1 = make_version(mnt_doc, hans, "1.0", "MNT_Antrieb_v1.pdf", "application/pdf",
                      b"%PDF-1.4 mock montage drawing content",
                      "Erstversion", datetime.utcnow() - timedelta(days=45),
                      extracted_text="MONTAGEZEICHNUNG Antriebseinheit\nAnzugsmoment M10: 46 Nm\nM12: 79 Nm\nEinbaulage: Horizontal",
                      is_current=True)
mnt_doc.current_version_id = mnt_v1.id
db.flush()

# 4) Key-Anweisung
awi_doc = Document(project_id=proj_a.id, doc_type=DocType.key_anweisung,
                   name="Arbeitsanweisung Wartung", status=DocumentStatus.current)
db.add(awi_doc)
db.flush()
awi_v1 = make_version(awi_doc, lisa, "1.0", "AWI_Wartung_Foerderband.pdf", "application/pdf",
                      b"%PDF-1.4 arbeitsanweisung wartung content",
                      "Erstversion", datetime.utcnow() - timedelta(days=40),
                      extracted_text="ARBEITSANWEISUNG: Wartung Förderbandanlage\nSchritt 1: Anlage abschalten\nWARNUNG: Spannungsfreiheit prüfen!\nSchritt 2: Keilriemenspannung prüfen\nSchritt 3: Lager abschmieren\nIntervall: alle 500 Betriebsstunden",
                      is_current=True)
awi_doc.current_version_id = awi_v1.id
db.flush()

# ── Demo: Steuerungsschrank SK-200 ───────────────────────────────────────────
bsz_doc = Document(project_id=proj_b.id, doc_type=DocType.bestückzeichnung,
                   name="Bestückplan Hauptplatine", status=DocumentStatus.current)
db.add(bsz_doc)
db.flush()
bsz_v1 = make_version(bsz_doc, hans, "1.0", "BSZ_Hauptplatine_Rev_A.pdf", "application/pdf",
                      b"%PDF-1.4 Bestueckzeichnung Platine Rev A",
                      "Rev A – Erstversion", datetime.utcnow() - timedelta(days=20),
                      extracted_text="BESTÜCKPLAN Hauptplatine SK-200\nRev A\nSMD-Bauteile: 142\nTHT-Bauteile: 18\nReferenzpunkt: X=5mm Y=5mm",
                      is_current=True)
bsz_doc.current_version_id = bsz_v1.id
db.flush()

# ── Demo: Hydraulikpresse HY-50 ──────────────────────────────────────────────
hstl_doc = Document(project_id=proj_c.id, doc_type=DocType.stückliste,
                    name="Hydraulik-Stückliste HY-50", status=DocumentStatus.current)
db.add(hstl_doc)
db.flush()

hy_bom_v1 = [
    ["10", "HY-001", "Hydraulikzylinder 50t",    "1", "Stk"],
    ["20", "HY-002", "Hydraulikpumpe 15kW",       "1", "Stk"],
    ["30", "HY-003", "Druckventil 350 bar",       "2", "Stk"],
    ["40", "HY-004", "Hydraulikschlauch DN16",    "5", "m"],
    ["50", "HY-005", "Ölbehälter 100L",           "1", "Stk"],
    ["60", "HY-006", "Manometer 0-400 bar",       "2", "Stk"],
]
hstl_v1 = make_version(hstl_doc, lisa, "1.0", "STL_HY50_v1.0.csv", "text/csv",
                       bom_to_csv(hy_bom_v1), "Erstversion",
                       datetime.utcnow() - timedelta(days=10),
                       extracted_data=bom_extracted(hy_bom_v1),
                       is_current=True)
hstl_doc.current_version_id = hstl_v1.id
db.flush()

# ── Activity logs ─────────────────────────────────────────────────────────────
logs = [
    ActivityLog(user_id=hans.id, action="upload", entity_type="document_version",
                entity_id=stl_v1.id, metadata_={"filename": stl_v1.file_name, "version": "1.0", "doc_type": "stückliste"},
                created_at=datetime.utcnow() - timedelta(days=60)),
    ActivityLog(user_id=lisa.id, action="upload", entity_type="document_version",
                entity_id=stl_v2.id, metadata_={"filename": stl_v2.file_name, "version": "1.1", "doc_type": "stückliste"},
                created_at=datetime.utcnow() - timedelta(days=30)),
    ActivityLog(user_id=hans.id, action="upload", entity_type="document_version",
                entity_id=zng_v1.id, metadata_={"filename": zng_v1.file_name, "version": "1.0", "doc_type": "zeichnung"},
                created_at=datetime.utcnow() - timedelta(days=55)),
    ActivityLog(user_id=lisa.id, action="upload", entity_type="document_version",
                entity_id=zng_v2.id, metadata_={"filename": zng_v2.file_name, "version": "1.1", "doc_type": "zeichnung"},
                created_at=datetime.utcnow() - timedelta(days=5)),
    ActivityLog(user_id=hans.id, action="upload", entity_type="document_version",
                entity_id=stl_v3.id, metadata_={"filename": stl_v3.file_name, "version": "1.2", "doc_type": "stückliste"},
                created_at=datetime.utcnow() - timedelta(days=2)),
    ActivityLog(user_id=lisa.id, action="upload", entity_type="document_version",
                entity_id=hstl_v1.id, metadata_={"filename": hstl_v1.file_name, "version": "1.0", "doc_type": "stückliste"},
                created_at=datetime.utcnow() - timedelta(days=10)),
]
db.add_all(logs)
db.commit()

print("Seed: done!")
print("  Users:     admin / h.mueller / l.schmidt  (Passwort: demo1234)")
print("  Customers: ACME Maschinenbau GmbH, TechnoKraft AG")
print("  Projects:  3 Projekte mit 7 Dokumenten und 9 Versionen")
db.close()
