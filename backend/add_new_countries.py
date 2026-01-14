from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.global_data import Country, Certification, RegulatoryMatrix, Technology

def add_data():
    db = SessionLocal()
    try:
        # 1. Countries
        new_countries = [
            {"name": "Dominican Republic", "iso_code": "DOM"},
            {"name": "Guyana", "iso_code": "GUY"},
            {"name": "Haiti", "iso_code": "HTI"},
            {"name": "Guatemala", "iso_code": "GTM"},
            {"name": "Suriname", "iso_code": "SUR"},
            {"name": "Venezuela", "iso_code": "VEN"},
            {"name": "Angola", "iso_code": "AGO"},
            {"name": "Gambia", "iso_code": "GMB"},
        ]
        
        country_objs = {}
        for c_data in new_countries:
            country = db.query(Country).filter(Country.iso_code == c_data["iso_code"]).first()
            if not country:
                country = Country(**c_data)
                db.add(country)
                print(f"Adding country: {c_data['name']}")
            else:
                print(f"Country exists: {c_data['name']}")
                # Ensure name is updated if needed, or just use existing
            country_objs[c_data["iso_code"]] = country
        db.flush()

        # 2. Certifications
        new_certs = [
            {
                "name": "INDOTEL Type Approval",
                "authority_name": "Instituto Dominicano de las Telecomunicaciones",
                "description": "Approval often lifetime / unlimited. CE / FCC reports usually accepted as technical basis. Local certificate issued.",
                "iso_code": "DOM"
            },
            {
                "name": "NFMU Type Approval",
                "authority_name": "National Frequency Management Unit",
                "description": "CE / FCC test reports reused. No expiry in many cases.",
                "iso_code": "GUY"
            },
            {
                "name": "CONATEL Type Approval", 
                "authority_name": "Conseil National des Télécommunications",
                "description": "Approval validity often unlimited. Local registration required.",
                "iso_code": "HTI"
            },
            {
                "name": "SIT Type Approval",
                "authority_name": "Superintendencia de Telecomunicaciones",
                "description": "CE/FCC reports accepted. Local filing mandatory.",
                "iso_code": "GTM"
            },
            {
                "name": "TAS Type Approval",
                "authority_name": "Telecommunicatie Autoriteit Suriname",
                "description": "Type approval for radio equipment in Suriname.",
                "iso_code": "SUR"
            },
            {
                "name": "CONATEL Venezuela Approval",
                "authority_name": "Comisión Nacional de Telecomunicaciones",
                "description": "Strict import controls. Local representative required.",
                "iso_code": "VEN"
            },
            {
                "name": "INACOM Type Approval",
                "authority_name": "Instituto Angolano das Comunicações",
                "description": "Validity-based approval. Renewal required.",
                "iso_code": "AGO"
            },
            {
                "name": "PURA Type Approval",
                "authority_name": "Public Utilities Regulatory Authority",
                "description": "Type approval for telecommunications equipment.",
                "iso_code": "GMB"
            }
        ]

        cert_objs = {}
        for cert_data in new_certs:
            cert = db.query(Certification).filter(Certification.name == cert_data["name"]).first()
            if not cert:
                cert = Certification(
                    name=cert_data["name"],
                    authority_name=cert_data["authority_name"],
                    description=cert_data["description"]
                )
                db.add(cert)
                print(f"Adding certification: {cert_data['name']}")
            else:
                print(f"Certification exists: {cert_data['name']}")
            cert_objs[cert_data["iso_code"]] = cert
        db.flush()

        # 3. Regulatory Matrix
        # Map all radio technologies to these certifications for their respective countries
        technologies = db.query(Technology).all()
        # Filter for radio techs commonly requiring type approval
        radio_keywords = ["Wi-Fi", "Bluetooth", "Cellular", "NFC", "LoRa", "Zigbee", "GPS", "NB-IoT", "Thread", "UWB", "60GHz", "5G", "4G", "LTE"]
        target_techs = [t for t in technologies if any(k in t.name for k in radio_keywords)]
        
        if not target_techs: # Fallback if no specific keywords match, use all (some might be wired, but usually this DB is wireless focused)
             target_techs = technologies

        count = 0
        for iso_code, country in country_objs.items():
            cert = cert_objs.get(iso_code)
            if not cert: continue
            
            for tech in target_techs:
                # Check if rule exists
                exists = db.query(RegulatoryMatrix).filter(
                    RegulatoryMatrix.country_id == country.id,
                    RegulatoryMatrix.technology_id == tech.id,
                    RegulatoryMatrix.certification_id == cert.id
                ).first()
                
                if not exists:
                    rule = RegulatoryMatrix(
                        country_id=country.id,
                        technology_id=tech.id,
                        certification_id=cert.id,
                        is_mandatory=True
                    )
                    db.add(rule)
                    count += 1
        
        print(f"Adding {count} new regulatory rules...")
        db.commit()
        print("Data population completed successfully.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_data()
