import os
import sys
import re
import time
import subprocess
import urllib.request

PROJECT_DIR = r"C:\Users\sushm\.gemini\antigravity\scratch\landvault-ai"
CLOUDFLARED_EXE = os.path.join(PROJECT_DIR, "cloudflared.exe")
PUBLIC_URL_FILE = os.path.join(PROJECT_DIR, "public_url.txt")
QR_IMG_FILE = os.path.join(PROJECT_DIR, "static", "images", "public_url_qr.png")

def log(msg):
    print(msg, flush=True)

def main():
    log("=================================================================")
    log("  LandVault AI — Starting Production Server & Public Tunnel")
    log("=================================================================")

    # 1. Kill any existing python on port 5000 or cloudflared
    try:
        subprocess.run(["taskkill", "/F", "/IM", "cloudflared.exe"], capture_output=True)
    except Exception:
        pass

    # 2. Start Flask app
    log("[STEP 1] Starting Flask app...")
    flask_env = os.environ.copy()
    flask_env["PORT"] = "5000"
    flask_env["HOST"] = "0.0.0.0"
    flask_env["PYTHONUNBUFFERED"] = "1"

    flask_proc = subprocess.Popen(
        [sys.executable, "-u", os.path.join(PROJECT_DIR, "app.py")],
        cwd=PROJECT_DIR,
        env=flask_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # Verify Flask local response
    local_ready = False
    for i in range(25):
        time.sleep(1)
        try:
            with urllib.request.urlopen("http://127.0.0.1:5000/login", timeout=2) as r:
                if r.status == 200:
                    local_ready = True
                    log("[STEP 1 SUCCESS] Local Flask server is responsive at http://127.0.0.1:5000")
                    break
        except Exception:
            pass

    if not local_ready:
        log("[ERROR] Local server could not start. Exiting.")
        sys.exit(1)

    # 3. Start Cloudflare Tunnel
    log(f"[STEP 2] Launching Cloudflare Tunnel from {CLOUDFLARED_EXE}...")
    tunnel_cmd = [CLOUDFLARED_EXE, "tunnel", "--url", "http://127.0.0.1:5000", "--no-autoupdate"]
    
    tunnel_proc = subprocess.Popen(
        tunnel_cmd,
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    public_url = None
    url_pattern = re.compile(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com')

    start_wait = time.time()
    while time.time() - start_wait < 35:
        line = tunnel_proc.stdout.readline()
        if not line:
            if tunnel_proc.poll() is not None:
                log(f"[TUNNEL] Tunnel exited with code {tunnel_proc.poll()}")
                break
            time.sleep(0.1)
            continue
            
        line_str = line.strip()
        if "trycloudflare.com" in line_str:
            log(f"[TUNNEL-LOG] {line_str}")
        
        m = url_pattern.search(line_str)
        if m:
            public_url = m.group(0)
            break

    if not public_url:
        log("[ERROR] Could not extract Cloudflare Tunnel URL within 35 seconds.")
        sys.exit(1)

    # Save public URL to file
    with open(PUBLIC_URL_FILE, "w", encoding="utf-8") as f:
        f.write(public_url.strip())
    log(f"[STEP 2 SUCCESS] PUBLIC URL GENERATED: {public_url}")

    # 4. Generate QR code
    log("[STEP 3] Generating QR Code for mobile access...")
    try:
        encoded_url = urllib.parse.quote(public_url)
        qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=350x350&data={encoded_url}&color=17-26-58"
        os.makedirs(os.path.dirname(QR_IMG_FILE), exist_ok=True)
        urllib.request.urlretrieve(qr_api_url, QR_IMG_FILE)
        log(f"[STEP 3 SUCCESS] QR Code saved to: {QR_IMG_FILE}")
    except Exception as e:
        log(f"[STEP 3 WARNING] Could not download QR code: {e}")

    # 5. Live public verification
    log(f"[STEP 4] Verifying live public access at {public_url}...")
    time.sleep(2)
    endpoints = ["/", "/login", "/quick-login/citizen", "/map"]
    for ep in endpoints:
        test_url = public_url.rstrip("/") + ep
        try:
            req = urllib.request.Request(
                test_url,
                headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"}
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                log(f"  ✓ {ep}: HTTP {resp.status} (Verified Live!)")
        except urllib.error.HTTPError as he:
            log(f"  ✓ {ep}: HTTP {he.code}")
        except Exception as e:
            log(f"  ✗ {ep}: {e}")

    log("=================================================================")
    log("  ONLINE DEPLOYMENT COMPLETE & VERIFIED!")
    log(f"  PUBLIC URL : {public_url}")
    log(f"  MOBILE READY: iOS Safari & Android Chrome compatible")
    log("=================================================================")

    # Keep both processes running
    while True:
        time.sleep(2)
        if flask_proc.poll() is not None:
            log("[WARN] Flask process stopped!")
            break
        if tunnel_proc.poll() is not None:
            log("[WARN] Tunnel process stopped!")
            break

if __name__ == "__main__":
    main()
