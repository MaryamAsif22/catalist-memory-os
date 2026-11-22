"""
capture_screenshots.py - Automated Visual Telemetry & Screenshot Capture.
Uses Chrome DevTools Protocol (CDP) over WebSocket to capture pixel-perfect
visual assets for documentation and submission review.
"""

import os
import sys
import json
import time
import base64
import asyncio
import subprocess
import urllib.request
from pathlib import Path

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TARGET_URL = "http://localhost:8000"
OUTPUT_DIR = Path("docs/screenshots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

try:
    import websockets
except ImportError:
    print("[Error] 'websockets' library required.")
    sys.exit(1)


async def send_cmd(ws, msg_id, method, params=None):
    payload = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(payload))
    while True:
        resp = await ws.recv()
        data = json.loads(resp)
        if data.get("id") == msg_id:
            return data.get("result", {})


async def capture_all():
    print("[1/5] Launching Chrome Headless instance on port 9222...")
    proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=9222",
        "--disable-gpu",
        "--window-size=1440,950",
        "--hide-scrollbars",
        TARGET_URL
    ])
    
    time.sleep(2.5)

    try:
        # Get WebSocket Debugger URL
        tabs_data = urllib.request.urlopen("http://127.0.0.1:9222/json").read()
        tabs = json.loads(tabs_data)
        target_tab = next((t for t in tabs if t.get("type") == "page"), tabs[0])
        ws_url = target_tab["webSocketDebuggerUrl"]
        print(f"[2/5] Connected to Chrome CDP: {ws_url}")

        async with websockets.connect(ws_url, max_size=20_000_000) as ws:
            # Enable Page and Runtime
            await send_cmd(ws, 1, "Page.enable")
            await send_cmd(ws, 2, "Runtime.enable")
            await send_cmd(ws, 3, "Emulation.setDeviceMetricsOverride", {
                "width": 1440,
                "height": 950,
                "deviceScaleFactor": 1.5,
                "mobile": False
            })

            # Wait for content rendering
            await asyncio.sleep(2.0)

            # 1. Hero Overview
            print("[3/5] Capturing 01_hero_dashboard.png...")
            await send_cmd(ws, 4, "Runtime.evaluate", {
                "expression": "window.scrollTo(0, 0);"
            })
            await asyncio.sleep(0.5)
            shot1 = await send_cmd(ws, 5, "Page.captureScreenshot", {"format": "png"})
            (OUTPUT_DIR / "01_hero_dashboard.png").write_bytes(base64.b64decode(shot1["data"]))

            # 2. Benchmark Spotlight Console
            print("[3/5] Capturing 02_benchmark_console.png...")
            await send_cmd(ws, 6, "Runtime.evaluate", {
                "expression": "document.documentElement.classList.remove('scroll-smooth'); window.scrollTo(0, document.getElementById('benchmark').offsetTop - 20);"
            })
            await asyncio.sleep(0.8)
            shot2 = await send_cmd(ws, 7, "Page.captureScreenshot", {"format": "png"})
            (OUTPUT_DIR / "02_benchmark_console.png").write_bytes(base64.b64decode(shot2["data"]))

            # 3. TS3012 Executive Briefing Dossier
            print("[3/5] Capturing 03_executive_briefing.png...")
            await send_cmd(ws, 8, "Runtime.evaluate", {
                "expression": "window.scrollTo(0, document.getElementById('briefing').offsetTop - 20);"
            })
            await asyncio.sleep(0.8)
            shot3 = await send_cmd(ws, 9, "Page.captureScreenshot", {"format": "png"})
            (OUTPUT_DIR / "03_executive_briefing.png").write_bytes(base64.b64decode(shot3["data"]))

            # 4. Corpus Transcript Explorer
            print("[3/5] Capturing 04_corpus_explorer.png...")
            await send_cmd(ws, 10, "Runtime.evaluate", {
                "expression": "window.scrollTo(0, document.getElementById('database').offsetTop - 20);"
            })
            await asyncio.sleep(0.8)
            shot4 = await send_cmd(ws, 11, "Page.captureScreenshot", {"format": "png"})
            (OUTPUT_DIR / "04_corpus_explorer.png").write_bytes(base64.b64decode(shot4["data"]))

            # 5. Interactive Ghost Mascot Chat Interface
            print("[3/5] Capturing 05_ghost_chat_interface.png...")
            await send_cmd(ws, 12, "Runtime.evaluate", {
                "expression": """
                document.getElementById('ghost-chat-modal').classList.remove('hidden');
                """
            })
            await asyncio.sleep(0.8)
            shot5 = await send_cmd(ws, 13, "Page.captureScreenshot", {"format": "png"})
            (OUTPUT_DIR / "05_ghost_chat_interface.png").write_bytes(base64.b64decode(shot5["data"]))

        print("[4/5] All screenshots captured successfully!")

    finally:
        proc.kill()
        print("[5/5] Chrome headless instance closed.")


if __name__ == "__main__":
    asyncio.run(capture_all())
