import os
from PIL import Image, ImageDraw, ImageFont

SAMPLE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sample_docs')
os.makedirs(SAMPLE_DIR, exist_ok=True)

def draw_official_header(draw, width, title, doc_type_sub):
    # Border
    draw.rectangle([20, 20, width - 20, 1180], outline=(75, 63, 114), width=3)
    draw.rectangle([26, 26, width - 26, 1174], outline=(15, 139, 141), width=1)
    
    # Header background band
    draw.rectangle([28, 28, width - 28, 140], fill=(23, 26, 58))
    
    # Header Text
    draw.text((width // 2, 50), "GOVERNMENT LAND RECORD & REVENUE SYSTEM", fill=(247, 244, 234), anchor="mm")
    draw.text((width // 2, 80), title.upper(), fill=(242, 169, 59), anchor="mm")
    draw.text((width // 2, 110), f"OFFICIAL CERTIFIED EXTRACT — {doc_type_sub}", fill=(200, 215, 230), anchor="mm")
    
    # Watermark simulation (subtle grid pattern)
    for y in range(180, 1100, 60):
        draw.line([40, y, width - 40, y], fill=(240, 240, 235), width=1)
    for x in range(40, width - 40, 60):
        draw.line([x, 180, x, 1100], fill=(240, 240, 235), width=1)

def draw_table_row(draw, y, label, value, width, highlight=False, anomaly_tag=None):
    x_label = 50
    x_val = 300
    row_height = 42
    
    bg_fill = (254, 245, 230) if highlight else ((250, 250, 252) if (y // row_height) % 2 == 0 else (255, 255, 255))
    draw.rectangle([40, y, width - 40, y + row_height], fill=bg_fill, outline=(220, 225, 230), width=1)
    
    draw.text((x_label, y + 12), label, fill=(75, 63, 114))
    draw.text((x_val, y + 12), value, fill=(23, 26, 58))
    
    if anomaly_tag:
        draw.rectangle([width - 240, y + 6, width - 50, y + 34], fill=(255, 235, 235), outline=(217, 92, 92), width=1)
        draw.text((width - 145, y + 12), anomaly_tag, fill=(217, 92, 92), anchor="mm")

def create_sample_fresh_patta():
    width, height = 850, 1200
    img = Image.new('RGB', (width, height), color=(253, 251, 247))
    draw = ImageDraw.Draw(img)
    
    draw_official_header(draw, width, "Patta Passbook Record", "FORM NO. 1 (RULE 3)")
    
    y = 160
    draw.text((50, y), "RECORD DETAILS & EXTRACT SUMMARY", fill=(15, 139, 141))
    draw.text((width - 50, y), "Doc Ref: TN-SLM-2026-1004", fill=(100, 100, 120), anchor="ra")
    y += 30
    
    rows = [
        ("Owner Name", "Radhakrishnan K.", False, None),
        ("Survey Number", "184/2A", False, None),
        ("Patta Number", "63941", False, None),
        ("District", "Salem", False, None),
        ("Taluk", "Attur", False, None),
        ("Village", "Attur Rural", False, None),
        ("Land Area", "2.85 Acres", False, None),
        ("Document Type", "Patta Passbook", False, None),
        ("Document Date", "04-10-2026", False, None),
        ("Land Classification", "Ryotwari Dry Agricultural Land", False, None),
        ("Revenue Assessment", "INR 165.00 / Annum", False, None),
    ]
    
    for label, val, hi, tag in rows:
        draw_table_row(draw, y, label, val, width, hi, tag)
        y += 42
        
    # Cadastre Sketch
    y += 20
    draw.text((50, y), "CADASTRE SUB-DIVISION SKETCH (PARCEL 184/2A)", fill=(15, 139, 141))
    y += 30
    
    draw.rectangle([50, y, width - 50, y + 230], outline=(15, 139, 141), fill=(245, 250, 250), width=2)
    draw.polygon([(110, y + 40), (460, y + 25), (510, y + 195), (130, y + 185)], outline=(23, 26, 58), width=3)
    draw.line([(290, y + 30), (320, y + 190)], fill=(242, 169, 59), width=2)
    draw.text((200, y + 100), "Parcel 184/2A\n[ 2.85 Acres ]", fill=(23, 26, 58), align="center")
    draw.text((400, y + 100), "Parcel 184/2B\n[ Adjoining ]", fill=(100, 110, 120), align="center")
    
    y += 250
    draw.ellipse([80, y, 220, y + 140], outline=(22, 134, 91), width=3)
    draw.text((150, y + 50), "REVENUE\nSEAL\nCERTIFIED", fill=(22, 134, 91), align="center", anchor="mm")
    
    draw.text((width - 250, y + 40), "Digitally Authenticated by:\nRevenue Divisional Office, Salem\nDate: 04 Oct 2026", fill=(75, 63, 114))
    
    out_path = os.path.join(SAMPLE_DIR, "sample_patta_passbook_salem.png")
    img.save(out_path, quality=95)
    print(f"Created: {out_path}")

def create_sample_anomaly():
    width, height = 850, 1200
    img = Image.new('RGB', (width, height), color=(253, 251, 247))
    draw = ImageDraw.Draw(img)
    
    draw_official_header(draw, width, "Registered Sale Deed Excerpt", "SCHEDULE 'A' PROPERTY")
    
    y = 160
    draw.text((50, y), "SCHEDULE PROPERTY SPECIFICATION", fill=(15, 139, 141))
    draw.text((width - 50, y), "Doc Ref: TN-MDU-2026-0722", fill=(100, 100, 120), anchor="ra")
    y += 30
    
    rows = [
        ("Owner Name", "Meenakshi Sundaram", False, None),
        ("Survey Number", "92/3C2", True, "Format Review"),
        ("Patta Number", "71508", False, None),
        ("District", "Madurai", False, None),
        ("Taluk", "Vadipatti", False, None),
        ("Village", "Alanganallur", True, "Low Contrast OCR"),
        ("Land Area", "3.75 Acres", False, None),
        ("Document Type", "Sale Deed Excerpt", False, None),
        ("Document Date", "22-07-2026", False, None),
        ("Registration Sub-District", "Vadipatti SRO Book 1", False, None),
        ("Previous Document Ref", "Doc No. 1104 / 2014", False, None)
    ]
    
    for label, val, hi, tag in rows:
        draw_table_row(draw, y, label, val, width, hi, tag)
        y += 42
        
    y += 20
    draw.text((50, y), "BOUNDARY DESCRIPTION & CAUTIONARY ANNOTATIONS", fill=(217, 92, 92))
    y += 30
    
    draw.rectangle([50, y, width - 50, y + 230], outline=(217, 92, 92), fill=(255, 248, 248), width=2)
    draw.text((70, y + 25), "North by: Survey No. 45/1 Cart Track Road\nSouth by: S.No. 45/3 Canal Embankment\nEast by: Sub-division 45/2B2 Land of Soundararajan\nWest by: Main Highway Access Border", fill=(50, 50, 60))
    
    draw.rectangle([70, y + 120, width - 70, y + 200], fill=(254, 235, 235), outline=(217, 92, 92))
    draw.text((width // 2, y + 160), "REVENUE INSPECTOR NOTE: Complex sub-division 45/2B1. Ground demarcation survey check recommended.", fill=(217, 92, 92), anchor="mm")
    
    y += 250
    draw.ellipse([80, y, 220, y + 140], outline=(233, 162, 39), width=3)
    draw.text((150, y + 50), "PENDING\nINSPECTION\nSEAL", fill=(233, 162, 39), align="center", anchor="mm")
    
    draw.text((width - 250, y + 40), "Submitted for AI Processing:\nMadurai Revenue Division\nStatus: Manual Verification Recommended", fill=(75, 63, 114))

    out_path = os.path.join(SAMPLE_DIR, "sample_deed_with_anomaly.png")
    img.save(out_path, quality=95)
    print(f"Created: {out_path}")

def create_sample_duplicate():
    width, height = 850, 1200
    img = Image.new('RGB', (width, height), color=(253, 251, 247))
    draw = ImageDraw.Draw(img)
    
    draw_official_header(draw, width, "Family Partition Deed Document", "CLAIMING PARCEL 123/4A")
    
    y = 160
    draw.text((50, y), "PARTITION SCHEDULE B - SUBMITTED APPLICATION", fill=(15, 139, 141))
    draw.text((width - 50, y), "Doc Ref: TN-SLM-2026-0902", fill=(100, 100, 120), anchor="ra")
    y += 30
    
    rows = [
        ("Owner Name", "Ramesh Kumar S.", False, None),
        ("Survey Number", "123/4A", True, "Duplicate Survey"),
        ("Patta Number", "45892", True, "Duplicate Patta"),
        ("District", "Salem", False, None),
        ("Taluk", "Attur", False, None),
        ("Village", "Attur Rural", False, None),
        ("Land Area", "2.5 Acres", False, None),
        ("Document Type", "Partition Deed", False, None),
        ("Document Date", "02-09-2026", False, None),
        ("Co-Claimant", "Suresh Kumar S.", False, None),
        ("Prior Record Link", "Registered under Patta 45892", False, None)
    ]
    
    for label, val, hi, tag in rows:
        draw_table_row(draw, y, label, val, width, hi, tag)
        y += 42
        
    y += 20
    draw.text((50, y), "DUPLICATE DETECTION WARNING SUMMARY", fill=(242, 169, 59))
    y += 30
    
    draw.rectangle([50, y, width - 50, y + 230], outline=(242, 169, 59), fill=(255, 252, 242), width=2)
    draw.text((70, y + 30), "LANDVAULT AI DUPLICATE NOTICE:\nParcel Survey No. 123/4A under Patta No. 45892 in Attur Rural\nalready exists in Verified Land Vault (Record ID: LV-2026-00125).\nCross-checking is required before any title mutation.", fill=(75, 63, 114))
    
    y += 250
    draw.ellipse([80, y, 220, y + 140], outline=(15, 139, 141), width=3)
    draw.text((150, y + 50), "REVENUE\nSUB-DESK\nSALEM", fill=(15, 139, 141), align="center", anchor="mm")
    
    draw.text((width - 250, y + 40), "Verification Desk:\nRevenue District Salem\nCandidate Record for Review", fill=(75, 63, 114))

    out_path = os.path.join(SAMPLE_DIR, "sample_duplicate_parcel.png")
    img.save(out_path, quality=95)
    print(f"Created: {out_path}")

if __name__ == '__main__':
    create_sample_fresh_patta()
    create_sample_anomaly()
    create_sample_duplicate()
    print("All sample demo land documents regenerated.")
