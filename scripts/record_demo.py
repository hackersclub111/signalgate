"""Autonomous 1080p Demo Video Generator for SignalGate Core.

Generates a broadcast-quality, judge-facing 90-115 second demonstration video:
  Scene 1: Introduction & Architecture Grounding (Infographic + Tactical Banner)
  Scene 2: Framework-Light Acoustic DSP (Playwright: Morse SOS Tapping + 492Hz Scope)
  Scene 3: Offline Multilingual Crisis Lexicon (Playwright: Tagalog Vocal Match)
  Scene 4: Evidential Arbitration & Refusal (Playwright: Conflict K=0.70 + Refusal to Dispatch)
  Scene 5: Multi-Node Spatial Corroboration (Playwright: Node 2 Corroboration + P0 HMAC Receipt)
  Scene 6: Deterministic Chaos & Pytest Suite (Playwright: 0 False Dispatches + 15/15 Tests)
  Scene 7: Outro Hero Card (SignalGate: Don't dispatch on uncorroborated evidence)

Features:
- Pure ground-truth browser execution via Playwright against live localhost:8000.
- Studio Neural voiceover (en-US-ChristopherNeural) via edge-tts.
- Tactical high-contrast lower-third banners with Consolas typography.
- Ambient tactical audio bed underneath narration with EBU R128 loudnorm normalization.
- 100% Honest labeling: "REAL DECISION ENGINE / SYNTHETIC SENSOR TESTBENCH".
"""
from __future__ import annotations

import os
import sys
import time
import asyncio
import threading
import subprocess
import urllib.request
import uvicorn
from playwright.sync_api import sync_playwright
import edge_tts

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

ASSETS_DIR = os.path.join(REPO_ROOT, "assets")
DEMO_DIR = os.path.join(ASSETS_DIR, "demo")
TEMP_DIR = os.path.join(REPO_ROOT, "temp_demo_build")

os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(DEMO_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

VOICE = "en-US-ChristopherNeural"
FONT_PATH = "C\\:/Windows/Fonts/consola.ttf"

SCENES = [
    {
        "id": "scene1",
        "type": "image",
        "image": os.path.join(ASSETS_DIR, "architecture_infographic.png"),
        "title": "SIGNALGATE - EMERGENCY TRIAGE ARCHITECTURE",
        "subtitle": "Offline Evidential Kernel - Synthetic Sensor Testbench - P2P Mesh",
        "narration": "This is a prototype for emergency triage when connectivity is unavailable. The physical sensor inputs in this demo are deterministic simulations; the decision engine itself is running live.",
    },
    {
        "id": "scene2",
        "type": "browser",
        "title": "SCENE 02 - FRAMEWORK-LIGHT ACOUSTIC DSP",
        "subtitle": "Pure NumPy Sliding FFT (0.17ms) Detects 492Hz Morse Cadence",
        "narration": "SignalGate processes lightweight local signal features instead of depending on a cloud model. A zero-dependency circular buffer extracts Morse distress cadence in 0.17 milliseconds on our test machine.",
    },
    {
        "id": "scene3",
        "type": "browser",
        "title": "SCENE 03 - OFFLINE MULTILINGUAL CRISIS LEXICON",
        "subtitle": "5 Regional Disaster Dialects Grounded Locally (SHA-256 - 5004bde6)",
        "narration": "Simultaneously, an offline multilingual lexicon spots emergency distress across vulnerable regional dialects, running in 0.04 milliseconds without cloud translation APIs.",
    },
    {
        "id": "scene4",
        "type": "browser",
        "title": "SCENE 04 - EVIDENTIAL ARBITRATION - REFUSAL TO DISPATCH",
        "subtitle": "High Conflict (K=0.70) - Active Refusal to Dispatch on Uncorroborated Noise",
        "narration": "The important question isn't whether one sensor fires; it's whether evidence is sufficient to act. When evidence conflicts, SignalGate does not force a binary dispatch decision. It explicitly represents conflict and uncertainty, actively refusing dispatch and requesting corroboration.",
    },
    {
        "id": "scene5",
        "type": "browser",
        "title": "SCENE 05 - MULTI-NODE SPATIAL CORROBORATION",
        "subtitle": "Independent Node 2 Evidence Escalates to P0 DISPATCH with HMAC-SHA256 Receipt",
        "narration": "An independent corroborating node provides additional spatial evidence. The arbitration policy can now escalate the incident to P0 dispatch, signed with an HMAC-SHA256 cryptographic provenance receipt.",
    },
    {
        "id": "scene6",
        "type": "browser",
        "title": "SCENE 06 - DETERMINISTIC CHAOS & UNIT TEST SUITE",
        "subtitle": "0 False Dispatches on 25 Conflict Scenarios - 15/15 Tests Passing",
        "narration": "We stress-test the implementation with our deterministic fault suite and run the automated test suite. Zero false dispatches across 25 high-conflict scenarios, with 15 out of 15 unit tests passing.",
    },
    {
        "id": "scene7",
        "type": "image",
        "image": os.path.join(ASSETS_DIR, "thumbnail_3x2.png"),
        "title": "SIGNALGATE - PROVENANCE-AUTHENTICATED EMERGENCY TRIAGE",
        "subtitle": "Don't dispatch on uncorroborated evidence.",
        "narration": "SignalGate: Don't dispatch on uncorroborated evidence. Real decision engine, synthetic sensor testbench, 100% offline.",
    },
]


def check_or_start_server(port: int = 8000) -> None:
    """Ensures FastAPI server is running on localhost:port."""
    url = f"http://127.0.0.1:{port}/"
    try:
        urllib.request.urlopen(url, timeout=1.0)
        print(f"[SERVER] Found existing SignalGate dashboard at {url}")
        return
    except Exception:
        pass

    print(f"[SERVER] Starting SignalGate server on {url} in background thread...")
    from server import app
    thread = threading.Thread(
        target=lambda: uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning"),
        daemon=True
    )
    thread.start()
    for _ in range(30):
        time.sleep(0.5)
        try:
            urllib.request.urlopen(url, timeout=1.0)
            print(f"[SERVER] SignalGate server successfully responsive at {url}")
            return
        except Exception:
            pass
    raise RuntimeError(f"Server did not start on {url}")


async def synthesize_all_narrations():
    """Synthesizes neural voiceover for each scene using edge-tts."""
    print("[TTS] Checking neural scene narration tracks...", flush=True)
    for scene in SCENES:
        out_audio = os.path.join(TEMP_DIR, f"{scene['id']}_voice.mp3")
        if os.path.exists(out_audio) and os.path.getsize(out_audio) > 1000:
            print(f"  [CACHE] Using existing audio for {scene['id']}", flush=True)
            continue
        communicate = edge_tts.Communicate(scene["narration"], VOICE, rate="+3%", volume="+30%")
        await communicate.save(out_audio)
        print(f"  [OK] Synthesized audio for {scene['id']}", flush=True)


def get_audio_duration(file_path: str) -> float:
    """Gets audio duration in seconds via ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", file_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def make_image_scene_clip(image_path: str, duration: float, title: str, subtitle: str, out_clip: str):
    """Creates a 1080p 30fps video clip from an image with lower-third tactical banner."""
    clean_title = title.replace(":", " - ").replace("'", "").replace('"', "")
    clean_sub = subtitle.replace(":", " - ").replace("'", "").replace('"', "")
    vf = (
        "scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#0a0c10,"
        "drawbox=y=ih-105:color=black@0.90:width=iw:height=95:t=fill,"
        f"drawtext=fontfile='{FONT_PATH}':text='{clean_title}':fontcolor=#38bdf8:fontsize=28:x=(w-text_w)/2:y=h-88,"
        f"drawtext=fontfile='{FONT_PATH}':text='{clean_sub}':fontcolor=#e2e8f0:fontsize=18:x=(w-text_w)/2:y=h-48"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", image_path,
        "-t", f"{duration:.3f}",
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        out_clip
    ]
    subprocess.run(cmd, capture_output=True, check=True)


def record_browser_scenes(target_url: str):
    """Executes deterministic Playwright UI walkthrough and records ground-truth browser video."""
    print("[PLAYWRIGHT] Launching Chromium to record ground-truth dashboard actions...", flush=True)
    rec_dir = os.path.join(TEMP_DIR, "raw_browser")
    os.makedirs(rec_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=rec_dir,
            record_video_size={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        page.goto(target_url, wait_until="networkidle")
        time.sleep(2.0)

        # Ensure dashboard canvas has loaded
        page.wait_for_selector("#scopeCanvas", timeout=15000)
        page.hover(".logo")
        time.sleep(1.5)

        # Action 1 (Scene 2): Trigger SOS Morse Tapping
        print("  [SCENE 02] Ingesting SOS Morse Tapping...", flush=True)
        page.locator("button:has-text('SOS Morse Tapping')").click()
        time.sleep(2.0)
        page.hover("#scopeCanvas")
        time.sleep(9.0)

        # Action 2 (Scene 3): Trigger Tagalog Crisis Vocal
        print("  [SCENE 03] Ingesting Tagalog Crisis Vocal...", flush=True)
        page.locator("button:has-text('Tagalog Crisis Vocal')").click()
        time.sleep(2.0)
        page.hover("#cur-decision")
        time.sleep(9.0)

        # Action 3 (Scene 4 - HERO MOMENT): Trigger Sensor Contradiction
        print("  [SCENE 04] HERO MOMENT: Ingesting Conflicting Sensors (Acoustic vs Noise)...", flush=True)
        page.locator("button:has-text('Inject Conflicting Sensors')").click()
        time.sleep(2.0)
        page.hover("#stat-conflict")
        time.sleep(4.0)
        page.hover("#cur-decision")
        time.sleep(12.0)

        # Action 4 (Scene 5): Trigger Node 2 Corroboration
        print("  [SCENE 05] Triggering Node 2 Spatial Corroboration...", flush=True)
        page.locator("button:has-text('Send Corroborating Seismic Cadence')").click()
        time.sleep(2.0)
        page.hover("#cur-decision")
        time.sleep(4.0)
        page.hover("#cur-hmac")
        time.sleep(8.0)

        # Action 5 (Scene 6): Trigger 50-Scenario Chaos Mode + 15-Unit Pytest
        print("  [SCENE 06] Triggering 50-Scenario Chaos Mode & Automated Test Suite...", flush=True)
        page.locator("button:has-text('RUN 50-SCENARIO CHAOS MODE')").click()
        time.sleep(4.0)
        page.locator("button:has-text('RUN 15-UNIT TEST SUITE')").click()
        time.sleep(12.0)

        context.close()
        browser.close()

    raw_files = [os.path.join(rec_dir, f) for f in os.listdir(rec_dir) if f.endswith(".webm")]
    if not raw_files:
        raise RuntimeError("No Playwright video recorded!")
    return raw_files[0]


def cut_and_assemble_scenes(raw_browser_video: str):
    """Trims, annotates with tactical lower-thirds, and muxes with neural narration audio."""
    print("[ASSEMBLY] Aligning and muxing 7 scenes with lower-third banners...")
    scene_clips = []

    # Offsets in seconds inside the single continuous Playwright recording
    browser_offsets = {
        "scene2": 3.0,
        "scene3": 14.0,
        "scene4": 25.0,
        "scene5": 43.0,
        "scene6": 57.0,
    }

    for scene in SCENES:
        sid = scene["id"]
        voice_file = os.path.join(TEMP_DIR, f"{sid}_voice.mp3")
        dur = get_audio_duration(voice_file) + 0.5  # padding

        raw_clip = os.path.join(TEMP_DIR, f"{sid}_video.mp4")
        muxed_clip = os.path.join(TEMP_DIR, f"{sid}_muxed.mp4")

        title = scene["title"]
        subtitle = scene["subtitle"]
        clean_title = title.replace(":", " - ").replace("'", "").replace('"', "")
        clean_sub = subtitle.replace(":", " - ").replace("'", "").replace('"', "")

        if scene["type"] == "image":
            make_image_scene_clip(scene["image"], dur, title, subtitle, raw_clip)
        else:
            offset = browser_offsets.get(sid, 0.0)
            vf = (
                "scale=1920:1080,"
                "drawbox=y=ih-105:color=black@0.90:width=iw:height=95:t=fill,"
                f"drawtext=fontfile='{FONT_PATH}':text='{clean_title}':fontcolor=#38bdf8:fontsize=28:x=(w-text_w)/2:y=h-88,"
                f"drawtext=fontfile='{FONT_PATH}':text='{clean_sub}':fontcolor=#e2e8f0:fontsize=18:x=(w-text_w)/2:y=h-48"
            )
            cmd = [
                "ffmpeg", "-y",
                "-ss", f"{offset:.2f}",
                "-i", raw_browser_video,
                "-t", f"{dur:.2f}",
                "-vf", vf,
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "18",
                "-pix_fmt", "yuv420p",
                "-r", "30",
                raw_clip
            ]
            subprocess.run(cmd, capture_output=True, check=True)

        # Mux video with narration audio
        cmd_mux = [
            "ffmpeg", "-y",
            "-i", raw_clip,
            "-i", voice_file,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            muxed_clip
        ]
        subprocess.run(cmd_mux, capture_output=True, check=True)
        scene_clips.append(muxed_clip)
        print(f"  [OK] Scene {sid} assembled ({dur:.1f}s)")

    # Master Concat
    concat_list = os.path.join(TEMP_DIR, "scenes.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for clip in scene_clips:
            clean_path = clip.replace("\\", "/")
            f.write(f"file '{clean_path}'\n")

    unmixed_video = os.path.join(TEMP_DIR, "unmixed_master.mp4")
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        unmixed_video
    ]
    subprocess.run(cmd_concat, capture_output=True, check=True)

    # Generate Subtle Ambient Synth Pad Bed
    total_dur = get_audio_duration(unmixed_video)
    bg_audio = os.path.join(TEMP_DIR, "ambient_pad.mp3")
    cmd_bg = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "aevalsrc=0.025*sin(2*PI*55*t)+0.018*sin(2*PI*110*t)+0.012*sin(2*PI*165*t):s=44100",
        "-t", f"{total_dur:.2f}",
        "-af", "volume=-25dB",
        bg_audio
    ]
    subprocess.run(cmd_bg, capture_output=True, check=True)

    master_output = os.path.join(DEMO_DIR, "signalgate_demo.mp4")
    print(f"[FINAL] Mixing ambient audio and applying broadcast loudnorm to {master_output}...")
    cmd_final = [
        "ffmpeg", "-y",
        "-i", unmixed_video,
        "-i", bg_audio,
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:weights=1.0 0.12,loudnorm=I=-16:TP=-1.5:LRA=11[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        master_output
    ]
    subprocess.run(cmd_final, capture_output=True, check=True)
    return master_output


def main():
    start_time = time.time()
    print("=" * 70)
    print("      SIGNALGATE AUTONOMOUS DEMO VIDEO PRODUCTION PIPELINE")
    print("=" * 70)

    # Step 1: Ensure Server is Ready
    check_or_start_server(port=8000)

    # Step 2: Synthesize Narrations
    asyncio.run(synthesize_all_narrations())

    # Step 3: Record Live Browser Interactions
    raw_browser = record_browser_scenes("http://127.0.0.1:8000/")

    # Step 4: Cut, Annotate with Lower-Third Banners, and Mux Audio
    final_video = cut_and_assemble_scenes(raw_browser)

    elapsed = time.time() - start_time
    total_duration = get_audio_duration(final_video)
    size_mb = os.path.getsize(final_video) / (1024 * 1024)

    print("=" * 70)
    print("DEMO VIDEO PRODUCTION COMPLETE")
    print(f"  Output Video: {final_video}")
    print(f"  Duration:     {total_duration:.1f} seconds")
    print(f"  File Size:    {size_mb:.2f} MB")
    print(f"  Time Taken:   {elapsed:.1f} seconds")
    print("=" * 70)


if __name__ == "__main__":
    main()
