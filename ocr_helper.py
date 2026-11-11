import os
import sys
import json
import shutil
from PIL import Image

# Setup Tesseract binary path
TESSERACT_EXE = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSDATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tessdata")

if not os.path.exists(TESSERACT_EXE):
    fallback = shutil.which("tesseract")
    if fallback:
        TESSERACT_EXE = fallback

import pytesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE

def convert_pdf_to_images(pdf_path, out_dir):
    import pymupdf
    os.makedirs(out_dir, exist_ok=True)
    doc = pymupdf.open(pdf_path)
    page_images = []
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]

    for i in range(len(doc)):
        page = doc[i]
        pix = page.get_pixmap(dpi=200)
        img_name = f"{base_name}_page_{i+1}.png"
        img_path = os.path.join(out_dir, img_name)
        pix.save(img_path)
        page_images.append(img_path)
    
    doc.close()
    return page_images

def preprocess_image(input_path, output_path=None):
    import cv2
    import numpy as np

    if output_path is None:
        dir_name = os.path.dirname(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(dir_name, f"prep_{base_name}.png")

    img = cv2.imread(input_path)
    if img is None:
        return input_path

    # Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Bilateral filter for noise reduction while keeping edges sharp
    denoised = cv2.bilateralFilter(gray, 9, 75, 75)

    # Adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 2
    )

    cv2.imwrite(output_path, thresh)
    return output_path

def run_ocr(image_path, lang='eng+tam'):
    if os.path.exists(TESSDATA_DIR):
        os.environ['TESSDATA_PREFIX'] = TESSDATA_DIR
    
    # Verify if tam is in requested lang and available
    actual_lang = lang
    if 'tam' in actual_lang:
        tam_path = os.path.join(TESSDATA_DIR, "tam.traineddata")
        if not os.path.exists(tam_path):
            actual_lang = 'eng'

    img = Image.open(image_path)
    
    # Extract raw text
    text = pytesseract.image_to_string(img, lang=actual_lang)
    
    # Extract detailed TSV data for word confidences
    try:
        data = pytesseract.image_to_data(img, lang=actual_lang, output_type=pytesseract.Output.DICT)
        confidences = [int(c) for c in data.get('conf', []) if isinstance(c, (int, str)) and str(c).isdigit() and int(c) >= 0]
        words = [w for w in data.get('text', []) if w.strip()]
        avg_conf = (sum(confidences) / len(confidences)) if confidences else 70.0
    except Exception as e:
        confidences = []
        words = []
        avg_conf = 75.0

    return {
        "text": text,
        "mean_confidence": round(avg_conf, 1),
        "total_words": len(words)
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command provided"}))
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "pdf-to-images":
        pdf_file = sys.argv[2]
        out_directory = sys.argv[3] if len(sys.argv) > 3 else os.path.dirname(pdf_file)
        try:
            pages = convert_pdf_to_images(pdf_file, out_directory)
            print(json.dumps({"success": True, "pages": pages}))
        except Exception as e:
            print(json.dumps({"success": False, "error": str(e)}))

    elif cmd == "preprocess":
        in_file = sys.argv[2]
        out_file = sys.argv[3] if len(sys.argv) > 3 else None
        try:
            prep_file = preprocess_image(in_file, out_file)
            print(json.dumps({"success": True, "preprocessed_path": prep_file}))
        except Exception as e:
            print(json.dumps({"success": False, "error": str(e)}))

    elif cmd == "ocr":
        in_file = sys.argv[2]
        lang = sys.argv[3] if len(sys.argv) > 3 else "eng+tam"
        try:
            result = run_ocr(in_file, lang)
            print(json.dumps({"success": True, "result": result}))
        except Exception as e:
            print(json.dumps({"success": False, "error": str(e)}))

    else:
        print(json.dumps({"error": f"Unknown command: {cmd}"}))
        sys.exit(1)
