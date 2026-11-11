# LandVault AI – Intelligent Land Record Digitization and Validation System
### Project ID:  |

**LandVault AI** is a complete, modern, professional web application designed for government revenue administrations to digitize, extract, validate, verify, and search land records using AI-assisted computer vision, Tesseract OCR, heuristic cadastre validation, and cryptographic QR verification.

---

## 🏛️ 1. Core Purpose & Philosophy
The primary users are **Government / Revenue Officers** (Tahsildars, Revenue Divisional Officers, District Registrars) and secondary users are **Citizens / Land Owners**.

### The 9-Stage AI Ingestion & Verification Pipeline:
1. **Document Upload** (PDF / JPG / PNG up to 10MB)
2. **Document Classification** (Patta Passbook, Sale Deed, Partition Deed, Chitta)
3. **Image Preprocessing** (OpenCV adaptive thresholding, bilateral noise filtering, deskewing)
4. **OCR Extraction** (Tesseract OCR / PyMuPDF token recognition)
5. **Smart Field Identification** (Owner Name, Survey Number, Patta Number, District, Taluk, Village, Land Area, Document Date)
6. **Intelligent Validation** (Format regex checks, district revenue registry validation)
7. **Statistical Confidence Score** (Field-by-field percentage + overall weighted gauge)
8. **Anomaly & Duplicate Detection** (Identifies complex sub-divisions, low-contrast text, cadastral parcel overlap)
9. **Human Verification & Archival** (Officer review, remarks, cryptographic SHA-256 seal, QR verification generation)

> 
> The system strictly adheres to the principle: **AI assists, humans decide**.
> Terminology used throughout the UI:
> - *"Potential anomaly detected"*
> - *"Requires manual verification"*
> - *"AI-assisted validation"*
> - Never asserts legal guilt or fraud.

---

## 🎨 2. Visual Identity & Brand Concept
- **Theme**: *"Heritage + Digital Intelligence"*
- **Palette**:
  - **Primary**: Deep Indigo & Midnight Violet (`#171A3A`, `#4B3F72`, `#20243A`)
  - **Secondary**: Teal (`#0F8B8D`)
  - **Accent**: Saffron / Warm Amber (`#F2A93B`, `#E9A227`)
  - **Success**: Emerald (`#16865B`)
  - **Danger**: Coral Red (`#D95C5C`)
  - **Background**: Warm Cream & Off-White (`#F7F4EA`, `#FFFFFF`)
- **Visual Motif**: *"Digital Land Grid"* geometric cadastral SVG motif integrated across headers, login, cards, and reports.
- **Brand Slogan**: *"Digitize. Validate. Verify. — From scanned documents to trusted digital records."*

---

## 🔐 3. User Roles & Demo Credentials

| Role | Username / Email | Password | Access Highlights |
| :--- | :--- | :--- | :--- |
| **Revenue Officer** | `officer@landvault.gov.in` | `officer123` | Full dashboard, AI processing, Split-screen review, Approvals, Queue, Analytics, Audit logs |
| **Citizen / Land Owner** | `citizen@example.com` | `citizen123` | Fast Patta search, Survey lookup, Public QR verification, Report downloads |

*⚡ **Pro Tip**: The login screen includes **1-Click Quick Demo Login** buttons for instant access without typing.*

---

## 🚀 4. How to Run the Application on Windows

The server is currently running live on:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

### Option A: Using Python directly (Recommended)
```bash
cd "C:\Users\sushm\.gemini\antigravity\scratch\landvault-ai"
python app.py
```

### Option B: Using npm scripts
```bash
cd "C:\Users\sushm\.gemini\antigravity\scratch\landvault-ai"
npm start
```

### Running Test Suites
1. **Core Integration & Unit Suite (18 tests)**:
```bash
python test_app.py
# or: npm test
```

2. **Extended OCR & Citizen End-to-End Suite (7 tests)**:
```bash
python test_extended.py
# or: npm run test:extended
```

3. **Run All Suites Concurrently (25 tests total, 100% pass)**:
```bash
python test_app.py; python test_extended.py
# or: npm run test:all
```

---

## 🧭 5. Step-by-Step Demo Demo Walkthrough

1. **Login**:
   - Open `http://127.0.0.1:5000/login`.
   - Click **"Officer Ramesh"** under ⚡ 1-Click Demo Demo.
2. **Dashboard Overview**:
   - View KPI statistics cards: Total Records (1,250), Verified (980), Pending (170), Anomalies (65), Duplicates (35).
   - Inspect live charts: *Records Processed Over Time* (Line chart), *Verification Status* (Donut chart), and *Records by District* (Bar chart).
   - Observe the *Priority Verification Queue* summary (High 12, Medium 35, Low 123).
3. **Document Processing & AI Pipeline**:
   - Navigate to **"Document Processing"** in the sidebar.
   - Click on **"Sample 1: Standard Patta"** (or drag & drop your own scan/PDF).
   - Click **"Start AI Processing"**.
   - Watch the animated 9-stage pipeline progress in real-time.
4. **Split-Screen OCR Inspection**:
   - **Left**: Document Parchment Viewer with Zoom In (+), Zoom Out (-), and Reset controls.
   - **Right**:
     - Circular Confidence Gauge (92%).
     - Field-by-field breakdown with confidence badges (Owner 93%, Survey 91%, Patta 95%, etc.).
     - Editable input fields.
     - Intelligent Validation Checklist (all passed).
5. **Officer Approval & Verification**:
   - Check *"I have reviewed the extracted information"*.
   - Add optional remarks in the Officer Remarks box.
   - Click **"Approve Record"**.
   - Watch the record get cryptographically signed and saved as **VERIFIED**.
6. **Testing Anomaly Detection**:
   - Go back to **Document Processing** and select **"Sample 2: Document with Anomaly"**.
   - Click **"Start AI Processing"**.
   - Observe the **Potential Anomalies** alert card:
     * *⚠ Complex sub-division requires ground inspection*
     * *⚠ Village name confidence is low (62%)*
     * AI Recommendation: *"Potential anomaly detected. Manual verification recommended."*
7. **Testing Duplicate Detection**:
   - Select **"Sample 3: Duplicate Candidate"**.
   - Click **"Start AI Processing"**.
   - Observe the **Possible Duplicate Records** banner:
     * *Cadastral Similarity: 94% with existing record LV-2026-00125*
     * *Matching fields: Owner Name, Survey Number, Village, Land Area*
     * Direct 1-click button to *"View Existing Record"*.
8. **Smart Search & Patta Lookup**:
   - Open **Search Records** or the Citizen Portal.
   - Enter Patta `#45892` into the Quick Patta Search card.
   - Instantly inspect owner details, survey 123/4A, and verification status.
9. **Official Report Generation**:
   - Open **Reports** -> Click **"Generate Verification Certificate"**.
   - Click **"Print / Download PDF Certificate"** to view the clean printable layout with LandVault watermark and SHA-256 seal.
10. **Public QR Verification**:
    - Click **"QR Verification"** or open `http://127.0.0.1:5000/verify/LV-2026-00125`.
    - View the public digital authenticity certificate with live cryptographic hash.
11. **Multilingual Toggle**:
    - Click **"தமிழ்"** in the topbar language switcher.
    - All interface labels (Dashboard -> டாஷ்போர்டு, Land Records -> நில பதிவுகள், Owner -> உரிமையாளர் பெயர், etc.) switch seamlessly.
12. **Audit Trail**:
    - Open **Audit Trail** in the sidebar to review the tamper-evident chronological event log tracking every officer and AI action.

---

## 🛠️ 6. Technical Stack
- **Backend**: Python Flask 3.1, SQLite 3
- **OCR Engine**: Tesseract OCR / Pytesseract + PyMuPDF (`fitz`) for PDF rasterization
- **Computer Vision**: OpenCV (`cv2`) for bilateral denoising and adaptive thresholding; Pillow (`PIL`) for image handling
- **Frontend**: Semantic HTML5, CSS3 (Bespoke Heritage + Digital theme), Vanilla Modern JavaScript (ES6+)
- **Visualizations**: Chart.js 4.4
- **Security & Integrity**: Werkzeug password hashing, session role enforcement, SHA-256 cadastral stamping, file sanitization

---



