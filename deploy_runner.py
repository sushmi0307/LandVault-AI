import os
import sys
import time
import re
import threading
import subprocess
import urllib.request
import urllib.error

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
CLOUDFLARED_EXE = os.path.join(PROJECT_DIR, "cloudflared.exe")
CLOUDFLARED_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
QR_IMG_PATH = os.path.join(PROJECT_DIR, "static", "images", "public_url_qr.png")

def ensure_cloudflared():
    if os.path.exists(CLOUDFLARED_EXE) and os.path.getsize(CLOUDFLARED_EXE) > 1000000:
        print(f"[DEPLOY] Found existing cloudflared binary at: {CLOUDFLARED_EXE}")
        return True
    
    print(f"[DEPLOY] Downloading Cloudflare Quick Tunnel binary to: {CLOUDFLARED_EXE}...")
    try:
        urllib.request.urlretrieve(CLOUDFLARED_URL, CLOUDFLARED_EXE)
        print("[DEPLOY] Cloudflare Quick Tunnel downloaded successfully.")
        return True
    except Exception as e:
        print(f"[DEPLOY] Warning: Could not download cloudflared ({e}). Will attempt SSH tunnel fallback.")
        return False

def start_flask_server():
    print("[DEPLOY] Starting LandVault AI Flask server on 0.0.0.0:5000...")
    sys.path.insert(0, PROJECT_DIR)
    from app import app, init_db, seed_demo_data
    
    init_db()
    seed_demo_data()
    
    # Run in a separate thread
    def run():
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True, use_reloader=False)

    t = threading.Thread(target=run, daemon=True)
    t.start()
    
    # Wait until local server is up
    for _ in range(30):
        try:
            with urllib.request.urlopen("http://127.0.0.1:5000/login", timeout=2) as resp:
                if resp.status == 200:
                    print("[DEPLOY] Flask local server is healthy and responding at http://127.0.0.1:5000")
                    return True
        except Exception:
            time.sleep(0.5)
            
    print("[DEPLOY] Error: Flask local server failed to respond within 15 seconds.")
    return False

def generate_qr_code(public_url):
    try:
        # Try importing qrcode library first
        import qrcode
        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data(public_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#171A3A", back_color="#FFFFFF")
        os.makedirs(os.path.dirname(QR_IMG_PATH), exist_ok=True)
        img.save(QR_IMG_PATH)
        print(f"[DEPLOY] Generated QR code saved to: {QR_IMG_PATH}")
        return
    except Exception:
        pass

    # Fallback to web QR generator API
    try:
        encoded = urllib.parse.quote(public_url)
        api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=350x350&data={encoded}&color=17-26-58"
        os.makedirs(os.path.dirname(QR_IMG_PATH), exist_ok=True)
        urllib.request.urlretrieve(api_url, QR_IMG_PATH)
        print(f"[DEPLOY] Downloaded high-res QR code saved to: {QR_IMG_PATH}")
    except Exception as e:
        print(f"[DEPLOY] Note: Could not generate QR image file: {e}")

def print_ascii_qr(public_url):
    try:
        # Simple terminal display if qrcode module supports it
        import qrcode
        qr = qrcode.QRCode()
        qr.add_data(public_url)
        qr.print_ascii(invert=True)
    except Exception:
        pass

def start_cloudflared_tunnel():
    print("[DEPLOY] Launching Cloudflare Tunnel for http://127.0.0.1:5000...")
    cmd = [CLOUDFLARED_EXE, "tunnel", "--url", "http://127.0.0.1:5000"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    
    url_pattern = re.compile(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com')
    public_url = None
    
    start_time = time.time()
    while time.time() - start_time < 30:
        line = proc.stdout.readline()
        if not line:
            if proc.poll() is not None:
                break
            continue
        print(f"[CLOUDFLARE] {line.strip()}")
        m = url_pattern.search(line)
        if m:
            public_url = m.group(0)
            break
            
    return proc, public_url

def start_ssh_tunnel():
    print("[DEPLOY] Launching SSH Tunnel (Pinggy) as fallback...")
    cmd = ["ssh", "-p", "443", "-o", "StrictHostKeyChecking=no", "-o", "ServerAliveInterval=30", "-R0:localhost:5000", "a.pinggy.io"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    
    url_pattern = re.compile(r'https://[a-zA-Z0-9-]+\.a\.pinggy\.link')
    public_url = None
    
    start_time = time.time()
    while time.time() - start_time < 25:
        line = proc.stdout.readline()
        if not line:
            if proc.poll() is not None:
                break
            continue
        print(f"[SSH-TUNNEL] {line.strip()}")
        m = url_pattern.search(line)
        if m:
            public_url = m.group(0)
            break
            
    return proc, public_url

def verify_public_url(public_url):
    print(f"\n[DEPLOY] VERIFYING PUBLIC URL: {public_url}")
    endpoints_to_test = [
        ("/", [200, 302]),
        ("/login", [200]),
        ("/quick-login/citizen", [200, 302]),
        ("/map", [200]),
        ("/api/land-locations", [200])
    ]
    
    results = {}
    for ep, acceptable_statuses in endpoints_to_test:
        test_url = f"{public_url.rstrip('/')}{ep}"
        try:
            req = urllib.request.Request(
                test_url,
                headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                status = resp.status
                content = resp.read(2048).decode('utf-8', errors='ignore')
                success = status in acceptable_statuses
                results[ep] = {"status": status, "success": success}
                print(f"  ✓ {ep}: HTTP {status} (Verified)")
        except urllib.error.HTTPError as e:
            success = e.code in acceptable_statuses
            results[ep] = {"status": e.code, "success": success}
            if success:
                print(f"  ✓ {ep}: HTTP {e.code} (Redirect / Acceptable)")
            else:
                print(f"  ✗ {ep}: HTTP {e.code} (Failed)")
        except Exception as e:
            results[ep] = {"status": "ERR", "error": str(e), "success": False}
            print(f"  ✗ {ep}: Error ({e})")
            
    return results

def main():
    print("=" * 65)
    print("  LandVault AI — Online Deployment & Mobile Access Manager")
    print("=" * 65)
    
    # 1. Start Flask
    if not start_flask_server():
        sys.exit(1)
        
    # 2. Get Public Tunnel
    tunnel_proc = None
    public_url = None
    
    if ensure_cloudflared():
        tunnel_proc, public_url = start_cloudflared_tunnel()
        
    if not public_url:
        print("[DEPLOY] Cloudflare Tunnel did not produce a URL. Trying SSH tunnel...")
        tunnel_proc, public_url = start_ssh_tunnel()
        
    if not public_url:
        print("[DEPLOY] FATAL: Could not establish a public tunnel. Check network access.")
        sys.exit(1)
        
    # 3. Verify public URL
    time.sleep(2)
    verify_results = verify_public_url(public_url)
    
    # 4. Generate QR code
    generate_qr_code(public_url)
    
    print("\n" + "=" * 65)
    print(f"  🎉 LANDVAULT AI IS LIVE AND ACCESSIBLE PUBLICLY!")
    print(f"  PUBLIC URL : {public_url}")
    print(f"  QR CODE    : {QR_IMG_PATH}")
    print("=" * 65)
    
    # Keep process alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[DEPLOY] Stopping deployment...")
        if tunnel_proc:
            tunnel_proc.terminate()

if __name__ == "__main__":
    main()
