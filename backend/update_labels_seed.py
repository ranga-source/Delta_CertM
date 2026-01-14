
import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.global_data import Certification

def update_labels():
    db = SessionLocal()
    try:
        print("Updating certifications with label info...")
        
        # 1. FCC Part 15
        fcc = db.query(Certification).filter(Certification.name.like("%FCC%")).all()
        for cert in fcc:
            cert.branding_image_url = "https://www.fcc.gov/sites/default/files/fcc-logo-black-2020.svg"
            cert.labeling_requirements = """
**FCC Labeling Requirements:**
1. **Placement**: The FCC ID must be visible on the exterior of the product.
2. **Text**: Must include "This device complies with Part 15 of the FCC Rules..."
3. **E-Labeling**: Permitted for devices with integral screens.
            """.strip()
            print(f"Updated {cert.name}")

        # 2. CE
        ce = db.query(Certification).filter(Certification.name == "CE").first()
        if ce:
            ce.branding_image_url = "http://images.seeklogo.com/logo-png/0/1/ce-marking-logo-png_seeklogo-99.png"
            ce.labeling_requirements = """
**CE Marking Requirements:**
1. **Size**: The CE mark must be at least 5mm vertically.
2. **Visibility**: Must be visible, legible, and indelible.
3. **Packaging**: If impossible on product, must be on packaging and documents.
            """.strip()
            print(f"Updated {ce.name}")

        # 3. WPC (India)
        wpc = db.query(Certification).filter(Certification.name == "WPC").first()
        if wpc:
            wpc.branding_image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6s8v4_Qj0h8w3_q_5a7_0_1_2_3_4_5" # Placeholder
            wpc.labeling_requirements = """
**WPC ETA Labeling:**
1. **ETA Number**: Must display "ETA-SD-YYYY/MMXX" issued by WPC.
2. **Placement**: On product label or manual.
            """.strip()
            print(f"Updated {wpc.name}")

        db.commit()
        print("Successfully updated certification labels! ✓")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_labels()
