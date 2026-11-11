/**
 * LANDVAULT AI — CORE JAVASCRIPT & MULTILINGUAL SYSTEM
 * Complete Tamil & English Dual Language Architecture
 */

// Comprehensive Multilingual Translation Dictionary (Natural, readable Tamil Unicode)
const TRANSLATIONS = {
  en: {
    // Navigation & Workspace Sections
    dashboard: "Dashboard",
    document_processing: "Document Processing",
    verification_queue: "Verification Queue",
    land_records: "Land Records",
    search: "Search Records",
    analytics: "Analytics",
    reports: "Reports",
    audit_trail: "Audit Trail",
    settings: "Settings",
    nav_revenue_workspace: "Revenue Workspace",
    nav_citizen_services: "Citizen Services",
    nav_records_analytics: "Records & Analytics",
    nav_home: "Home",
    nav_search_record: "Search Land Record",
    nav_qr_verification: "QR Verification",
    land_map: "Land Map",
    nav_download_report: "Download Report",
    search_placeholder: "Search by owner, survey number, patta number or village...",
    notifications_alerts: "Notifications & Alerts",
    notifications_new: "3 New",
    btn_citizen_view: "Citizen View",
    btn_officer_view: "Officer View",
    role_citizen: "Citizen",
    role_officer: "Officer",
    btn_logout: "Sign Out",
    my_land_records: "My Land Records",
    upload_document: "Upload Document",
    view_document: "View Document",
    download: "Download",
    search_action: "Search",
    verification_status: "Verification Status",
    survey_number_lbl: "Survey Number",
    patta_number_lbl: "Patta Number",
    district_lbl: "District",
    taluk_lbl: "Taluk",
    village_lbl: "Village",
    land_area_lbl: "Land Area",
    logout_lbl: "Logout",
    no_records_found: "No Records Found",
    upload_successful: "Upload Successful",

    // Login Page
    login_welcome_back: "Welcome Back",
    login_subtitle: "Sign in to access your land records.",
    login_email_username: "Email or Username",
    login_email_placeholder: "Enter email or username",
    login_password: "Password",
    login_password_placeholder: "Enter password",
    login_btn_submit: "Sign In",
    login_or_try_demo: "OR TRY DEMO",
    login_demo_officer_title: "Revenue Officer",
    login_demo_officer_name: "Ramesh V. Sundaram",
    login_demo_citizen_title: "Citizen / Land Owner",
    login_demo_citizen_name: "Ananya R. Sharma",
    login_feature_1_title: "Smart Document Processing",
    login_feature_1_desc: "Extract important details from scanned land documents.",
    login_feature_2_title: "Secure Land Records",
    login_feature_2_desc: "Organize and access land information digitally.",
    login_feature_3_title: "Reliable Verification",
    login_feature_3_desc: "Identify missing or inconsistent details for verification.",
    login_heading: "Your Land, Your Rights, Digitally Secured.",
    login_description: "A smarter way to digitize, validate, and manage land records securely.",
    login_badge_tag: "Government Revenue Digital Portal · தமிழ்நாடு",

    // Citizen Portal Hero
    cit_hero_tag: "Government Revenue Digital Services · தமிழ்நாடு நில ஆவணங்கள்",
    cit_hero_title: "Citizen Land Portal — Land Record Services",
    cit_hero_desc: "Upload your Patta, Chitta, or other land documents directly from your computer. Our local AI OCR extracts information without any external API keys. Review and correct extracted fields before submitting for official Revenue Officer review.",
    cit_logged_in_label: "LOGGED IN CITIZEN",
    cit_district_label: "District:",

    // Citizen Quick Search
    cit_search_title: "Quick Patta & Land Record Verification",
    cit_search_desc: "Check official revenue status by Patta number",
    cit_search_placeholder: "Enter Patta Number (e.g. 45892 or 63941)",
    cit_search_btn: "Lookup Patta",

    // Citizen Upload & OCR
    cit_upload_title: "Upload & Digitize Land Document (Local AI OCR)",
    cit_upload_desc: "Select a Patta or Chitta file from your computer (PDF, PNG, JPG). Local OCR will read the document offline without any API keys.",
    cit_presets_title: "⚡ Quick Test Presets (Instant 1-Click Verification):",
    cit_preset_passbook: "📄 Patta Passbook (Image)",
    cit_preset_chitta: "📑 Chitta Extract (Digital PDF)",
    cit_preset_scanned: "🖨 Scanned Patta (Scanned PDF)",
    cit_dropzone_title: "Drag & Drop Your Land Record or Click to Browse",
    cit_dropzone_sub: "Supported formats: PDF (text or scanned), PNG, JPG, JPEG (Max 15MB)",
    cit_browse_btn: "Browse Files from Computer",
    cit_preset_info: "Preset Land Document · Local AI Verification",
    cit_extract_btn: "Extract Document Text (Local OCR)",
    cit_progress_text: "Running local Tesseract OCR & extracting land record attributes...",
    cit_preview_title: "Uploaded Document Preview",
    cit_btn_reset: "Reset",
    cit_review_title: "Review Extracted Information",
    cit_review_desc: "Verify and correct details before submitting to Revenue Officer",
    cit_quality_label: "EXTRACTION QUALITY",

    // Form Field Labels
    owner_name: "Owner Name",
    survey_number: "Survey Number",
    subdivision_number: "Subdivision Number",
    patta_number: "Patta Number",
    district: "District",
    taluk: "Taluk",
    village: "Village",
    land_area: "Land Area",
    doc_type: "Document Type",
    doc_date: "Document Date",
    cit_remarks_label: "Citizen Remarks",

    // Form Field Placeholders
    ph_owner_name: "Full Owner Name",
    ph_survey_number: "Survey Number (e.g. 184/2A)",
    ph_subdivision_number: "Subdivision (e.g. 2A)",
    ph_patta_number: "Patta Number",
    ph_district: "District",
    ph_taluk: "Taluk",
    ph_village: "Village",
    ph_land_area: "Area (e.g. 2.5 Acres)",
    ph_doc_type: "Patta Passbook / Chitta",
    ph_doc_date: "DD-MM-YYYY",
    ph_remarks: "Purpose (e.g. Verification / Ownership Update)",

    // Notice & Submission
    notice_title: "Notice:",
    cit_notice_prefix: "Submitting will record this document in the official Revenue Verification Queue under reference ",
    cit_notice_suffix: "An authorized officer will inspect and cross-verify with village registers.",
    cit_submit_btn: "✓ Submit Record for Official Officer Review",
    cit_submitting_btn: "Submitting Record...",

    // Citizen Records Table
    cit_table_title: "My Submitted Records & Revenue Verification Status",
    cit_table_desc: "Track status of documents submitted for verification (Pending, Verified, Needs Review, Rejected)",
    th_record_id: "Record ID",
    th_owner_name: "Owner Name",
    th_survey_no: "Survey No",
    th_patta_no: "Patta No",
    th_village_district: "Village / District",
    th_submission_date: "Submission Date",
    th_status: "Status",
    th_officer_remarks: "Officer Remarks",
    th_seal: "Verification Seal",
    btn_view_qr: "View QR Seal",
    badge_pending_officer: "Pending Officer",
    empty_submitted_records: "No submitted records found. Upload a document to get started.",

    // Status Badges & Pills
    status: "Status",
    status_verified: "VERIFIED",
    status_pending: "PENDING",
    status_needs_review: "NEEDS REVIEW",
    status_potential_anomaly: "POTENTIAL ANOMALY",
    status_duplicate_candidate: "DUPLICATE CANDIDATE",
    status_rejected: "REJECTED",
    status_pending_review: "Pending Review",
    verified: "Verified",
    pending: "Pending",
    needs_review: "Needs Review",
    potential_anomaly: "Potential Anomaly",
    duplicate_candidate: "Duplicate Candidate",
    rejected: "Rejected",

    // Record Detail Page
    detail_title: "Land Record Details",
    detail_subtitle: "Review the information extracted from the uploaded land document.",
    doc_info_header: "Document Information",
    ocr_confidence: "OCR Confidence",
    processing_status: "Processing Status",
    btn_print_pdf: "Print / Save as PDF",
    btn_back_records: "Back to Records",
    btn_back_home: "Return to Citizen Portal",
    val_not_available: "Not available",
    val_not_found: "Not found in document",
    val_not_specified: "Not specified",
    detail_note_title: "Important:",
    detail_note_body: "These details depend on the uploaded document and OCR results. Missing information is not guessed. OCR confidence measures text extraction quality and does not prove ownership or document authenticity. This page is not an official government certificate.",

    // Reports & Certificate Page
    reports_title: "Reports & Verification Certificates",
    reports_subtitle: "Official certified extract generation and digital verification certificates.",
    cert_title: "OFFICIAL LAND RECORD VERIFICATION CERTIFICATE",
    cert_subtitle: "Government Revenue Administration · Cadastral Authenticity Report",
    cert_extract_badge: "OFFICIAL VERIFICATION EXTRACT",
    cert_ref: "Record Reference",
    cert_seal_title: "Cryptographic SHA-256 Seal",
    cert_disclaimer_title: "Legal Attestation:",
    cert_disclaimer_body: "This certificate is generated by LandVault AI following automated OCR extraction and Revenue Officer verification. Verification status reflects comparison against authoritative Tamil Nadu Cadastral Gazetteers and Taluk registers.",

    // Search Page & Records Page
    search_page_title: "Search Land Records",
    search_page_subtitle: "Search available records using an owner name, survey number, patta number, or record ID.",
    search_docs_title: "Search Documents",
    search_input_ph: "Enter owner name, survey number or record ID",
    btn_search: "Search",
    search_results_title: "Search Results",
    th_action: "Action",
    btn_view: "View",
    no_matching_records: "No matching records found.",
    all_records_title: "All Records",
    btn_upload_doc: "+ Upload Document",
    btn_view_details: "View Details",

    // Public QR Verification Page
    verify_public_tag: "DEPARTMENT OF REVENUE & LAND ADMINISTRATION • GOVT VERIFIED",
    verify_public_title: "Verify Digital Land Record",
    verify_public_sub: "Public cryptographic authenticity certificate",
    verify_public_qr_caption: "Scan QR to verify this record on any smartphone or kiosk.",
    verify_public_id_label: "Record Identifier",
    verify_public_pattadhar: "Registered Pattadhar",
    verify_public_cadastral: "Cadastral Survey Number",
    verify_public_extent: "Registered Extent / Area",
    verify_public_jurisdiction: "District Jurisdiction",
    verify_public_taluk_village: "Taluk / Village",
    verify_public_officer: "Verified By Officer",
    verify_public_date: "Verification Date",
    verify_public_tamper_seal: "Tamper-Evident SHA-256 Digital Certificate Seal",
    verify_public_print_btn: "Print Verification Stamp",
    verify_public_return_btn: "Return to Citizen Portal",

    // Interactive Alerts & Dynamic Texts
    alert_select_file: "Please select or upload a document file first.",
    alert_ocr_error: "OCR Processing Error: ",
    alert_submit_success_prefix: "Document successfully submitted! Reference ID: ",
    alert_status_pending: "Status: PENDING.",
    alert_submit_error: "Submission error: ",
    alert_submit_failed: "Failed to submit document: ",
    alert_search_failed: "Search failed: ",
    msg_record_found: "Official Record Found: ",
    label_owner: "Owner: ",
    label_survey: "Survey No: ",
    label_patta: "Patta: ",
    label_location: "Location: ",
    label_area: "Area: ",
    label_status: "Status: ",
    btn_view_full_details: "View Complete Record Details",
    msg_no_record_found: "No registered cadastral record found matching Patta #",
    msg_no_record_suffix: ". Please check the number or upload your document above.",
    banner_attention: "Attention:",
    processing_ocr_btn: "Processing OCR...",
    overall_confidence: "Overall Extraction Confidence",
    approve_record: "Approve Record",
    reject_record: "Reject",
    send_review: "Send for Review",
    edit_fields: "Edit Fields",
    scan_qr: "Scan QR to verify this record",
    digital_vault: "Digital Land Vault",
    officer_verification: "Officer Verification",
    manual_review_rec: "Requires manual verification",
    potential_anomaly_detected: "Potential anomaly detected",
    ai_assisted_val: "AI-assisted validation"
  },

  ta: {
    // Navigation & Workspace Sections
    dashboard: "முகப்புப் பலகை",
    document_processing: "ஆவண செயலாக்கம்",
    verification_queue: "சரிபார்ப்பு வரிசை",
    land_records: "நிலப் பதிவுகள்",
    search: "பதிவுகள் தேடல்",
    analytics: "பகுப்பாய்வு",
    reports: "அறிக்கைகள்",
    audit_trail: "தணிக்கை பதிவு",
    settings: "அமைப்புகள்",
    nav_revenue_workspace: "வருவாய் பணியிடம்",
    nav_citizen_services: "குடிமக்கள் சேவைகள்",
    nav_records_analytics: "பதிவுகள் & பகுப்பாய்வு",
    nav_home: "முகப்பு",
    nav_search_record: "நிலப் பதிவுகள் தேடல்",
    nav_qr_verification: "QR சரிபார்ப்பு",
    land_map: "நில வரைபடம்",
    nav_download_report: "அறிக்கையைப் பதிவிறக்குக",
    search_placeholder: "உரிமையாளர் பெயர், சர்வே எண், பட்டா எண் அல்லது கிராமம் மூலம் தேடுக...",
    notifications_alerts: "அறிவிப்புகள் & எச்சரிக்கைகள்",
    notifications_new: "3 புதியவை",
    btn_citizen_view: "குடிமகன் பார்வை",
    btn_officer_view: "அதிகாரி பார்வை",
    role_citizen: "குடிமகன்",
    role_officer: "வருவாய்த்துறை அதிகாரி",
    btn_logout: "வெளியேறவும்",
    my_land_records: "எனது நிலப் பதிவுகள்",
    upload_document: "ஆவணத்தைப் பதிவேற்றவும்",
    view_document: "ஆவணத்தைப் பார்க்கவும்",
    download: "பதிவிறக்கவும்",
    search_action: "தேடுக",
    verification_status: "சரிபார்ப்பு நிலை",
    survey_number_lbl: "சர்வே எண்",
    patta_number_lbl: "பட்டா எண்",
    district_lbl: "மாவட்டம்",
    taluk_lbl: "வட்டம்",
    village_lbl: "கிராமம்",
    land_area_lbl: "நிலத்தின் பரப்பளவு",
    logout_lbl: "வெளியேறவும்",
    no_records_found: "பதிவுகள் எதுவும் கிடைக்கவில்லை",
    upload_successful: "ஆவணம் வெற்றிகரமாகப் பதிவேற்றப்பட்டது",

    // Login Page
    login_welcome_back: "மீண்டும் வருக",
    login_subtitle: "உங்கள் நிலப் பதிவுகளை அணுக உள்நுழைக.",
    login_email_username: "மின்னஞ்சல் அல்லது பயனர் பெயர்",
    login_email_placeholder: "மின்னஞ்சல் அல்லது பயனர் பெயரை உள்ளிடவும்",
    login_password: "கடவுச்சொல்",
    login_password_placeholder: "கடவுச்சொல்லை உள்ளிடவும்",
    login_btn_submit: "உள்நுழைக",
    login_or_try_demo: "அல்லது டெமோவை முயற்சிக்கவும்",
    login_demo_officer_title: "வருவாய்த்துறை அதிகாரி",
    login_demo_officer_name: "ரமேஷ் வி. சுந்தரம்",
    login_demo_citizen_title: "குடிமகன் / நில உரிமையாளர்",
    login_demo_citizen_name: "அனன்யா ஆர். சர்மா",
    login_feature_1_title: "நுண்ணறிவு ஆவண செயலாக்கம்",
    login_feature_1_desc: "ஸ்கேன் செய்யப்பட்ட நில ஆவணங்களிலிருந்து முக்கிய விவரங்களைப் பிரித்தெடுக்கவும்.",
    login_feature_2_title: "பாதுகாப்பான நிலப் பதிவுகள்",
    login_feature_2_desc: "நில விவரங்களை டிஜிட்டல் முறையில் பாதுகாப்பாக ஒழுங்கமைத்து அணுகவும்.",
    login_feature_3_title: "நம்பகமான சரிபார்ப்பு",
    login_feature_3_desc: "சரிபார்ப்பிற்காக விடுபட்ட அல்லது முரண்பாடான விவரங்களைக் கண்டறியவும்.",
    login_heading: "உங்கள் நிலம், உங்கள் உரிமைகள், டிஜிட்டல் முறையில் பாதுகாக்கப்படுகின்றன.",
    login_description: "நில ஆவணங்களை பாதுகாப்பாக டிஜிட்டல் மயமாக்கி, சரிபார்த்து நிர்வகிக்கும் நவீன வழி.",
    login_badge_tag: "அரசு வருவாய் டிஜிட்டல் போர்ட்டல் · தமிழ்நாடு",

    // Citizen Portal Hero
    cit_hero_tag: "அரசு வருவாய் டிஜிட்டல் சேவைகள் · தமிழ்நாடு நில ஆவணங்கள்",
    cit_hero_title: "குடிமக்கள் நில போர்ட்டல் — நில ஆவண சேவைகள்",
    cit_hero_desc: "உங்கள் பட்டா, சிட்டா அல்லது பிற நில ஆவணங்களை உங்கள் கணினியிலிருந்து நேரடியாகப் பதிவேற்றவும். வெளிப்புற API சாவிகள் இல்லாமல் எங்களின் உள்ளூர் AI OCR தகவல்களைப் பிரித்தெடுக்கிறது. அதிகாரப்பூர்வ வருவாய்த்துறை அதிகாரி மதிப்பாய்வுக்கு சமர்ப்பிக்கும் முன், பிரித்தெடுக்கப்பட்ட விவரங்களைச் சரிபார்த்து திருத்தலாம்.",
    cit_logged_in_label: "உள்நுழைந்துள்ள குடிமகன்",
    cit_district_label: "மாவட்டம்:",

    // Citizen Quick Search
    cit_search_title: "விரைவு பட்டா & நில ஆவண சரிபார்ப்பு",
    cit_search_desc: "பட்டா எண் மூலம் அதிகாரப்பூர்வ வருவாய் நிலையைச் சரிபார்க்கவும்",
    cit_search_placeholder: "பட்டா எண்ணை உள்ளிடவும் (எ.கா. 45892 அல்லது 63941)",
    cit_search_btn: "பட்டாவைத் தேடுக",

    // Citizen Upload & OCR
    cit_upload_title: "நில ஆவணத்தைப் பதிவேற்றி டிஜிட்டல் மயமாக்குங்கள் (உள்ளூர் AI OCR)",
    cit_upload_desc: "உங்கள் கணினியிலிருந்து பட்டா அல்லது சிட்டா கோப்பைத் தேர்ந்தெடுக்கவும் (PDF, PNG, JPG). உள்ளூர் OCR இணையம் மற்றும் API சாவிகள் இல்லாமல் ஆவணத்தைப் படிக்கும்.",
    cit_presets_title: "⚡ உடனடி சோதனை மாதிரிகள் (1-கிளிக் சரிபார்ப்பு):",
    cit_preset_passbook: "📄 பட்டா பாஸ்புக் (படம்)",
    cit_preset_chitta: "📑 சிட்டா சான்று (டிஜிட்டல் PDF)",
    cit_preset_scanned: "🖨 ஸ்கேன் செய்த பட்டா (ஸ்கேன் PDF)",
    cit_dropzone_title: "உங்கள் நில ஆவணத்தை இழுத்து விடவும் அல்லது தேர்ந்தெடுக்க கிளிக் செய்யவும்",
    cit_dropzone_sub: "ஆதரிக்கப்படும் வடிவங்கள்: PDF (உரை அல்லது ஸ்கேன்), PNG, JPG, JPEG (அதிகபட்சம் 15MB)",
    cit_browse_btn: "கணினியிலிருந்து கோப்புகளைத் தேர்வுசெய்க",
    cit_preset_info: "மாதிரி நில ஆவணம் · உள்ளூர் AI சரிபார்ப்பு",
    cit_extract_btn: "ஆவண உரையைப் பிரித்தெடுக்கவும் (உள்ளூர் OCR)",
    cit_progress_text: "உள்ளூர் Tesseract OCR இயக்கப்பட்டு நில ஆவண விவரங்கள் பிரித்தெடுக்கப்படுகின்றன...",
    cit_preview_title: "பதிவேற்றப்பட்ட ஆவணத்தின் முன்னோட்டம்",
    cit_btn_reset: "மீட்டமை",
    cit_review_title: "பிரித்தெடுக்கப்பட்ட தகவல்களைச் சரிபார்க்கவும்",
    cit_review_desc: "வருவாய்த்துறை அதிகாரியிடம் சமர்ப்பிக்கும் முன் விவரங்களைச் சரிபார்த்து திருத்தவும்",
    cit_quality_label: "பிரித்தெடுத்தல் தரம்",

    // Form Field Labels
    owner_name: "உரிமையாளர் பெயர்",
    survey_number: "சர்வே எண்",
    subdivision_number: "உட்பிரிவு எண்",
    patta_number: "பட்டா எண்",
    district: "மாவட்டம்",
    taluk: "வட்டம்",
    village: "கிராமம்",
    land_area: "நிலத்தின் பரப்பளவு",
    doc_type: "ஆவண வகை",
    doc_date: "ஆவண தேதி",
    cit_remarks_label: "குடிமகன் குறிப்புகள்",

    // Form Field Placeholders
    ph_owner_name: "முழு உரிமையாளர் பெயர்",
    ph_survey_number: "சர்வே எண் (எ.கா. 184/2A)",
    ph_subdivision_number: "உட்பிரிவு (எ.கா. 2A)",
    ph_patta_number: "பட்டா எண்",
    ph_district: "மாவட்டம்",
    ph_taluk: "வட்டம்",
    ph_village: "கிராமம்",
    ph_land_area: "பரப்பளவு (எ.கா. 2.5 ஏக்கர்)",
    ph_doc_type: "பட்டா பாஸ்புக் / சிட்டா",
    ph_doc_date: "நாள்-மாதம்-ஆண்டு (DD-MM-YYYY)",
    ph_remarks: "நோக்கம் (எ.கா. சரிபார்ப்பு / உரிமை மாற்றம்)",

    // Notice & Submission
    notice_title: "அறிவிப்பு:",
    cit_notice_prefix: "சமர்ப்பிப்பதன் மூலம் இந்த ஆவணம் அதிகாரப்பூர்வ வருவாய் சரிபார்ப்பு வரிசையில் குறிப்பு எண் ",
    cit_notice_suffix: "அங்கீகரிக்கப்பட்ட அதிகாரி கிராமப் பதிவேடுகளுடன் ஆய்வு செய்து சரிபார்ப்பார்.",
    cit_submit_btn: "✓ அதிகாரியின் அதிகாரப்பூர்வ மதிப்பாய்வுக்கு சமர்ப்பிக்கவும்",
    cit_submitting_btn: "பதிவு சமர்ப்பிக்கப்படுகிறது...",

    // Citizen Records Table
    cit_table_title: "எனது சமர்ப்பிக்கப்பட்ட பதிவுகள் & சரிபார்ப்பு நிலை",
    cit_table_desc: "சரிபார்ப்புக்குச் சமர்ப்பிக்கப்பட்ட ஆவணங்களின் நிலையைக் கண்காணிக்கவும் (நிலுவையில், சரிபார்க்கப்பட்டது, மறுஆய்வு தேவை, நிராகரிக்கப்பட்டது)",
    th_record_id: "பதிவு எண்",
    th_owner_name: "உரிமையாளர் பெயர்",
    th_survey_no: "சர்வே எண்",
    th_patta_no: "பட்டா எண்",
    th_village_district: "கிராமம் / மாவட்டம்",
    th_submission_date: "சமர்ப்பிக்கப்பட்ட தேதி",
    th_status: "சரிபார்ப்பு நிலை",
    th_officer_remarks: "அதிகாரியின் குறிப்புகள்",
    th_seal: "சரிபார்ப்பு முத்திரை",
    btn_view_qr: "QR முத்திரையைக் காண்க",
    badge_pending_officer: "அதிகாரி சரிபார்ப்பில்",
    empty_submitted_records: "பதிவுகள் எதுவும் கிடைக்கவில்லை. தொடங்க ஒரு ஆவணத்தைப் பதிவேற்றவும்.",

    // Status Badges & Pills
    status: "சரிபார்ப்பு நிலை",
    status_verified: "சரிபார்க்கப்பட்டது",
    status_pending: "நிலுவையில்",
    status_needs_review: "மறுஆய்வு தேவை",
    status_potential_anomaly: "சாத்தியமான முரண்பாடு",
    status_duplicate_candidate: "நகல் பதிவு சாத்தியம்",
    status_rejected: "நிராகரிக்கப்பட்டது",
    status_pending_review: "மறுஆய்வில் நிலுவை",
    verified: "சரிபார்க்கப்பட்டது",
    pending: "நிலுவையில்",
    needs_review: "மறுஆய்வு தேவை",
    potential_anomaly: "சாத்தியமான முரண்பாடு",
    duplicate_candidate: "நகல் பதிவு சாத்தியம்",
    rejected: "நிராகரிக்கப்பட்டது",

    // Record Detail Page
    detail_title: "நிலப் பதிவு விவரங்கள்",
    detail_subtitle: "பதிவேற்றப்பட்ட நில ஆவணத்திலிருந்து பிரித்தெடுக்கப்பட்ட தகவல்களைச் சரிபார்க்கவும்.",
    doc_info_header: "ஆவணத் தகவல்கள்",
    ocr_confidence: "OCR நம்பிக்கை அளவு",
    processing_status: "செயலாக்க நிலை",
    btn_print_pdf: "அச்சிடுக / PDF ஆக சேமிக்க",
    btn_back_records: "பதிவுகளுக்குத் திரும்பு",
    btn_back_home: "குடிமக்கள் போர்ட்டலுக்குத் திரும்பு",
    val_not_available: "கிடைக்கவில்லை",
    val_not_found: "ஆவணத்தில் காணப்படவில்லை",
    val_not_specified: "குறிப்பிடப்படவில்லை",
    detail_note_title: "முக்கிய குறிப்பு:",
    detail_note_body: "இந்த விவரங்கள் பதிவேற்றப்பட்ட ஆவணம் மற்றும் OCR முடிவுகளை அடிப்படையாகக் கொண்டவை. விடுபட்ட தகவல்கள் தானாக நிரப்பப்படாது. OCR நம்பிக்கை அளவு உரை பிரித்தெடுத்தலின் தரத்தை மட்டுமே குறிக்கிறது; இது உரிமை அல்லது ஆவணத்தின் உண்மைத்தன்மையை நிரூபிக்காது. இந்தப் பக்கம் அதிகாரப்பூர்வ அரசு சான்றிதழ் அல்ல.",

    // Reports & Certificate Page
    reports_title: "அறிக்கைகள் & சரிபார்ப்பு சான்றிதழ்கள்",
    reports_subtitle: "அதிகாரப்பூர்வ சான்றளிக்கப்பட்ட சான்றிதழ் மற்றும் டிஜிட்டல் சரிபார்ப்பு சான்றிதழ்கள்.",
    cert_title: "அதிகாரப்பூர்வ நில ஆவண சரிபார்ப்பு சான்றிதழ்",
    cert_subtitle: "அரசு வருவாய் நிர்வாகம் · நில உண்மைத்தன்மை அறிக்கை",
    cert_extract_badge: "அதிகாரப்பூர்வ சரிபார்ப்பு சான்று",
    cert_ref: "பதிவு குறிப்பு எண்",
    cert_seal_title: "கிரிப்டோகிராஃபிக் SHA-256 முத்திரை",
    cert_disclaimer_title: "சட்டப்பூர்வ சான்றளிப்பு:",
    cert_disclaimer_body: "இந்தச் சான்றிதழ் தானியங்கி OCR பிரித்தெடுத்தல் மற்றும் வருவாய்த்துறை அதிகாரி சரிபார்ப்பிற்குப் பிறகு LandVault AI ஆல் உருவாக்கப்பட்டது. சரிபார்ப்பு நிலை தமிழ்நாடு அரசிதழ்கள் மற்றும் வட்டப் பதிவேடுகளுடன் ஒப்பிடுவதைப் பிரதிபலிக்கிறது.",

    // Search Page & Records Page
    search_page_title: "நிலப் பதிவுகள் தேடல்",
    search_page_subtitle: "உரிமையாளர் பெயர், சர்வே எண், பட்டா எண் அல்லது பதிவு அடையாள எண் கொண்டு தேடுங்கள்.",
    search_docs_title: "ஆவணங்களைத் தேடுக",
    search_input_ph: "உரிமையாளர் பெயர், சர்வே எண் அல்லது பதிவு எண் உள்ளிடவும்",
    btn_search: "தேடுக",
    search_results_title: "தேடல் முடிவுகள்",
    th_action: "செயல்",
    btn_view: "காண்க",
    no_matching_records: "பொருத்தமான பதிவுகள் எதுவும் கிடைக்கவில்லை.",
    all_records_title: "அனைத்து பதிவுகள்",
    btn_upload_doc: "+ ஆவணத்தைப் பதிவேற்றவும்",
    btn_view_details: "விவரங்களைக் காண்க",

    // Public QR Verification Page
    verify_public_tag: "வருவாய் மற்றும் நில நிர்வாகத் துறை • அரசு சரிபார்க்கப்பட்டது",
    verify_public_title: "டிஜிட்டல் நில ஆவணத்தைச் சரிபார்க்கவும்",
    verify_public_sub: "பொது கிரிப்டோகிராஃபிக் உண்மைத்தன்மை சான்றிதழ்",
    verify_public_qr_caption: "ஸ்மார்ட்போன் அல்லது கியோஸ்க்கில் இந்த ஆவணத்தைச் சரிபார்க்க QR குறியீட்டை ஸ்கேன் செய்யவும்.",
    verify_public_id_label: "பதிவு அடையாள எண்",
    verify_public_pattadhar: "பதிவுசெய்யப்பட்ட பட்டாதாரர்",
    verify_public_cadastral: "சர்வே எண்",
    verify_public_extent: "பதிவு செய்யப்பட்ட பரப்பளவு",
    verify_public_jurisdiction: "மாவட்ட எல்லை",
    verify_public_taluk_village: "வட்டம் / கிராமம்",
    verify_public_officer: "சரிபார்த்த அதிகாரி",
    verify_public_date: "சரிபார்க்கப்பட்ட தேதி",
    verify_public_tamper_seal: "பாதுகாப்பான SHA-256 டிஜிட்டல் சான்றிதழ் முத்திரை",
    verify_public_print_btn: "சரிபார்ப்பு முத்திரையை அச்சிடுக",
    verify_public_return_btn: "குடிமக்கள் போர்ட்டலுக்குத் திரும்பு",

    // Interactive Alerts & Dynamic Texts
    alert_select_file: "தயவுசெய்து முதலில் ஒரு ஆவணக் கோப்பைத் தேர்ந்தெடுக்கவும் அல்லது பதிவேற்றவும்.",
    alert_ocr_error: "OCR செயலாக்கப் பிழை: ",
    alert_submit_success_prefix: "ஆவணம் வெற்றிகரமாகச் சமர்ப்பிக்கப்பட்டது! குறிப்பு எண்: ",
    alert_status_pending: "நிலை: நிலுவையில்.",
    alert_submit_error: "சமர்ப்பிப்பதில் பிழை: ",
    alert_submit_failed: "ஆவணத்தைச் சமர்ப்பிக்க முடியவில்லை: ",
    alert_search_failed: "தேடல் தோல்வியடைந்தது: ",
    msg_record_found: "அதிகாரப்பூர்வ பதிவு கண்டறியப்பட்டது: ",
    label_owner: "உரிமையாளர்: ",
    label_survey: "சர்வே எண்: ",
    label_patta: "பட்டா எண்: ",
    label_location: "இடம்: ",
    label_area: "நிலப்பரப்பு: ",
    label_status: "நிலை: ",
    btn_view_full_details: "முழு விவரங்களையும் பார்க்கவும்",
    msg_no_record_found: "பட்டா #",
    msg_no_record_suffix: "-க்குரிய பதிவு எதுவும் கிடைக்கவில்லை. தயவுசெய்து எண்ணைச் சரிபார்க்கவும் அல்லது மேலே உள்ள படிவத்தில் உங்கள் ஆவணத்தைப் பதிவேற்றவும்.",
    banner_attention: "கவனத்திற்கு:",
    processing_ocr_btn: "OCR செயலாக்கப்படுகிறது...",
    overall_confidence: "ஒட்டுமொத்த பிரித்தெடுத்தல் நம்பிக்கை",
    approve_record: "பதிவை அங்கீகரிக்கவும்",
    reject_record: "நிராகரி",
    send_review: "மறுஆய்வுக்கு அனுப்பு",
    edit_fields: "புலங்களை திருத்து",
    scan_qr: "சரிபார்க்க QR குறியீட்டை ஸ்கேன் செய்யவும்",
    digital_vault: "டிஜிட்டல் நில பெட்டகம்",
    officer_verification: "அதிகாரி சரிபார்ப்பு",
    manual_review_rec: "கைமுறை சரிபார்ப்பு தேவைப்படுகிறது",
    potential_anomaly_detected: "சாத்தியமான முரண்பாடு கண்டறியப்பட்டது",
    ai_assisted_val: "செயற்கை நுண்ணறிவு உதவி சரிபார்ப்பு"
  }
};

let currentLang = localStorage.getItem('landvault_lang') || 'en';

// Global translation accessor
window.t = function(key, fallback = '') {
  if (TRANSLATIONS[currentLang] && TRANSLATIONS[currentLang][key] !== undefined) {
    return TRANSLATIONS[currentLang][key];
  }
  if (TRANSLATIONS.en && TRANSLATIONS.en[key] !== undefined) {
    return TRANSLATIONS.en[key];
  }
  return fallback;
};

window.getLang = function() {
  return currentLang;
};

// Set and switch language dynamically across DOM
function setLanguage(lang) {
  if (lang !== 'en' && lang !== 'ta') lang = 'en';
  currentLang = lang;
  try {
    localStorage.setItem('landvault_lang', lang);
    document.cookie = "landvault_lang=" + lang + ";path=/;max-age=31536000";
    document.documentElement.lang = lang;
    try {
      fetch('/api/set-language/' + encodeURIComponent(lang)).catch(() => {});
    } catch (_) {}
  } catch (e) {
    console.warn("Storage warning:", e);
  }

  // 1. Update toggle button active states
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.lang === lang);
  });

  // 2. Translate textContent for [data-i18n]
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (TRANSLATIONS[lang] && TRANSLATIONS[lang][key] !== undefined) {
      el.textContent = TRANSLATIONS[lang][key];
    }
  });

  // 3. Translate placeholders for [data-i18n-placeholder]
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    if (TRANSLATIONS[lang] && TRANSLATIONS[lang][key] !== undefined) {
      el.placeholder = TRANSLATIONS[lang][key];
    }
  });

  // 4. Translate titles for [data-i18n-title]
  document.querySelectorAll('[data-i18n-title]').forEach(el => {
    const key = el.getAttribute('data-i18n-title');
    if (TRANSLATIONS[lang] && TRANSLATIONS[lang][key] !== undefined) {
      el.title = TRANSLATIONS[lang][key];
    }
  });

  // 5. Translate aria-labels for [data-i18n-aria]
  document.querySelectorAll('[data-i18n-aria]').forEach(el => {
    const key = el.getAttribute('data-i18n-aria');
    if (TRANSLATIONS[lang] && TRANSLATIONS[lang][key] !== undefined) {
      el.setAttribute('aria-label', TRANSLATIONS[lang][key]);
    }
  });

  // 6. Translate status pills dynamically
  document.querySelectorAll('.status-pill').forEach(el => {
    if (!el.hasAttribute('data-raw-status')) {
      el.setAttribute('data-raw-status', el.textContent.trim());
    }
    const raw = el.getAttribute('data-raw-status').replace(/^✓\s*/, '').trim();
    const key = 'status_' + raw.toLowerCase().replace(/[\s-]/g, '_');
    if (TRANSLATIONS[lang] && TRANSLATIONS[lang][key]) {
      const prefix = el.textContent.includes('✓') ? '✓ ' : '';
      el.textContent = prefix + TRANSLATIONS[lang][key];
    } else if (lang === 'en') {
      const prefix = el.textContent.includes('✓') ? '✓ ' : '';
      el.textContent = prefix + raw;
    }
  });

  // 7. Dispatch event for page-specific dynamic widgets (e.g. citizen portal results)
  window.dispatchEvent(new CustomEvent('landvault:langchange', { detail: { lang: lang } }));
}

// Toast Notifications System
function showToast(message, type = 'success') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  
  const icon = type === 'success' ? '✓' : (type === 'warning' ? '⚠' : 'ℹ');
  toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(50px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Modal Helpers
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('show');
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('show');
  }
}

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  // Init language from storage or cookie
  const savedLang = localStorage.getItem('landvault_lang') || 'en';
  setLanguage(savedLang);

  // Attach language switcher button clicks
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      setLanguage(btn.dataset.lang);
    });
  });

  // Mobile Menu Toggle
  const mobileBtn = document.querySelector('.mobile-menu-btn');
  const sidebar = document.querySelector('.sidebar');
  if (mobileBtn && sidebar) {
    mobileBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      sidebar.classList.toggle('open');
    });

    document.addEventListener('click', (e) => {
      if (window.innerWidth <= 768 && sidebar.classList.contains('open')) {
        if (!sidebar.contains(e.target) && e.target !== mobileBtn) {
          sidebar.classList.remove('open');
        }
      }
    });

    sidebar.querySelectorAll('a.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        if (window.innerWidth <= 768) {
          sidebar.classList.remove('open');
        }
      });
    });
  }

  // Notification Bell Toggle
  const bellBtn = document.querySelector('.notif-toggle-btn');
  const notifMenu = document.querySelector('.notifications-menu');
  if (bellBtn && notifMenu) {
    bellBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      notifMenu.classList.toggle('show');
    });

    document.addEventListener('click', (e) => {
      if (!notifMenu.contains(e.target) && e.target !== bellBtn) {
        notifMenu.classList.remove('show');
      }
    });
  }

  // Close modals on overlay click or cancel button
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        overlay.classList.remove('show');
      }
    });
  });

  document.querySelectorAll('[data-close-modal]').forEach(btn => {
    btn.addEventListener('click', () => {
      const modalId = btn.getAttribute('data-close-modal');
      closeModal(modalId);
    });
  });
});
