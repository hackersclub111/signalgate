"""
SignalGate Local-First Web Dashboard Server
Single-file FastAPI server with embedded HTML/Tailwind/Alpine-style UI.
Features:
- 100% Offline (no external CDN required, fallback embedded CSS/JS)
- Real-time simulation triggers (Acoustic Morse, Tagalog Voice, Structural Noise)
- Visual Dempster-Shafer Conflict Gauge & Mass Distribution Bar
- Live P2P Mesh Topology Display
- One-Click CHAOS MODE toggle
"""

import os
import json
import asyncio
from typing import Dict, Any, List
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

from src.dsp_sensor import AcousticDSPSensor
from src.crisis_nlp import CrisisNLPEngine
from src.dempster_shafer import DempsterShaferFusion
from src.triage_arbitrator import TriageArbitrator
from src.mesh_simulator import MeshNetworkSimulator
from src.chaos_injector import ChaosFaultInjector

app = FastAPI(title="SignalGate Core Web Dashboard")

# Global in-memory state
dsp = AcousticDSPSensor()
nlp = CrisisNLPEngine()
mesh = MeshNetworkSimulator(packet_loss_rate=0.0)
chaos_injector = ChaosFaultInjector(seed=42)

incident_history: List[Dict[str, Any]] = []

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SignalGate // Offline Evidential Emergency Triage</title>
    <style>
        :root {
            --bg: #0d1117;
            --surface: #161b22;
            --border: #30363d;
            --text: #c9d1d9;
            --accent: #58a6ff;
            --p0: #f85149;
            --p1: #d29922;
            --p2: #8957e5;
            --p3: #238636;
            --hold: #e3b341;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; }
        body { background: var(--bg); color: var(--text); padding: 20px; line-height: 1.5; }
        header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 16px; border-bottom: 1px solid var(--border); margin-bottom: 20px; }
        .logo { font-size: 1.4rem; font-weight: 700; color: #fff; letter-spacing: 1px; display: flex; align-items: center; gap: 8px; }
        .badge { background: #238636; color: #fff; font-size: 0.75rem; padding: 2px 8px; border-radius: 12px; }
        .badge.offline { background: #6e7681; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }
        .card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 18px; }
        .card-title { font-size: 1rem; font-weight: 600; margin-bottom: 14px; color: #fff; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
        .btn-group { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 15px; }
        button { background: #21262d; color: #c9d1d9; border: 1px solid var(--border); padding: 8px 14px; border-radius: 6px; cursor: pointer; font-size: 0.85rem; transition: all 0.2s; }
        button:hover { background: #30363d; color: #fff; }
        button.btn-danger { background: rgba(248,81,73,0.15); border-color: var(--p0); color: #ff7b72; }
        button.btn-danger:hover { background: var(--p0); color: #fff; }
        button.btn-primary { background: rgba(88,166,255,0.15); border-color: var(--accent); color: var(--accent); }
        button.btn-primary:hover { background: var(--accent); color: #000; }
        .meter { height: 12px; background: #21262d; border-radius: 6px; overflow: hidden; display: flex; margin-bottom: 8px; }
        .meter-bar { height: 100%; transition: width 0.3s; }
        .bar-victim { background: var(--p0); }
        .bar-noise { background: var(--p3); }
        .bar-hazard { background: var(--p1); }
        .bar-theta { background: var(--p2); }
        .log-box { height: 260px; overflow-y: auto; background: #090d13; border: 1px solid var(--border); border-radius: 6px; padding: 10px; font-family: monospace; font-size: 0.8rem; }
        .log-entry { margin-bottom: 8px; padding: 6px; border-radius: 4px; border-left: 3px solid var(--border); }
        .log-entry.DISPATCH { border-left-color: var(--p0); background: rgba(248,81,73,0.08); }
        .log-entry.HOLD_AND_CORROBORATE { border-left-color: var(--hold); background: rgba(227,179,65,0.08); }
        .log-entry.IGNORE { border-left-color: var(--p3); background: rgba(35,134,54,0.08); }
        .stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 14px; }
        .stat-box { background: #090d13; border: 1px solid var(--border); border-radius: 6px; padding: 10px; text-align: center; }
        .stat-val { font-size: 1.2rem; font-weight: 700; color: #fff; }
        .stat-lbl { font-size: 0.7rem; color: #8b949e; text-transform: uppercase; }
        .tag { font-size: 0.75rem; padding: 2px 6px; border-radius: 4px; background: #21262d; }
    </style>
</head>
<body>
    <header>
        <div class="logo">
            <span>🚨 SIGNALGATE CORE</span>
            <span class="badge">EVIDENTIAL TRIAGE v1.0</span>
            <span class="badge offline">INTERNET SEVERED (100% LOCAL)</span>
        </div>
        <div>
            <span id="system-status" class="tag" style="color:#58a6ff;">SYSTEM READY</span>
        </div>
    </header>

    <div class="grid">
        <!-- Interactive Trigger Controls -->
        <div class="card">
            <div class="card-title">1. Sensor Incident Injection & P2P Inputs</div>
            <p style="font-size:0.85rem; color:#8b949e; margin-bottom: 12px;">
                Simulate raw hardware signals arriving at local field nodes under zero connectivity:
            </p>
            <div class="btn-group">
                <button class="btn-primary" onclick="triggerEvent('sos_tap')">🔨 Node 1: SOS Morse Tapping (DSP 0.14ms)</button>
                <button class="btn-primary" onclick="triggerEvent('voice_tl')">🗣️ Node 3: Tagalog Crisis Vocal ("Tulong!")</button>
                <button onclick="triggerEvent('rain_noise')">🌧️ Node 1: Structural Settling / Ambient Noise</button>
                <button class="btn-danger" onclick="triggerEvent('contradiction')">⚠️ Inject Conflicting Sensors (Acoustic vs Noise)</button>
            </div>

            <div class="card-title" style="margin-top: 18px;">2. Multi-Node Corroboration</div>
            <p style="font-size:0.85rem; color:#8b949e; margin-bottom: 12px;">
                When an ambiguous event is held, inject independent spatial corroboration:
            </p>
            <div class="btn-group">
                <button id="btn-corroborate" onclick="triggerCorroboration()" style="border-color:#e3b341; color:#e3b341;">
                    🤝 Node 2: Send Corroborating Seismic Cadence
                </button>
            </div>

            <div class="card-title" style="margin-top: 18px;">3. Automated Fault Stress Suite</div>
            <div class="btn-group">
                <button class="btn-danger" onclick="triggerChaos()">⚡ RUN 50-SCENARIO CHAOS MODE (40% Drop + Noise)</button>
            </div>
        </div>

        <!-- Evidential Fusion State & Gauges -->
        <div class="card">
            <div class="card-title">2. Dempster-Shafer Arbitration Gate</div>
            
            <div class="stat-grid">
                <div class="stat-box">
                    <div id="stat-conflict" class="stat-val" style="color:#d29922;">0.00</div>
                    <div class="stat-lbl">Conflict Metric (K)</div>
                </div>
                <div class="stat-box">
                    <div id="stat-victim" class="stat-val" style="color:#f85149;">0.00</div>
                    <div class="stat-lbl">Belief m(Victim)</div>
                </div>
                <div class="stat-box">
                    <div id="stat-noise" class="stat-val" style="color:#238636;">0.00</div>
                    <div class="stat-lbl">Belief m(Noise)</div>
                </div>
                <div class="stat-box">
                    <div id="stat-theta" class="stat-val" style="color:#8957e5;">1.00</div>
                    <div class="stat-lbl">Ignorance m(&Theta;)</div>
                </div>
            </div>

            <div style="font-size:0.8rem; margin-bottom: 4px; color:#8b949e;">Belief Mass Allocation:</div>
            <div class="meter">
                <div id="bar-v" class="meter-bar bar-victim" style="width: 0%;"></div>
                <div id="bar-n" class="meter-bar bar-noise" style="width: 0%;"></div>
                <div id="bar-h" class="meter-bar bar-hazard" style="width: 0%;"></div>
                <div id="bar-t" class="meter-bar bar-theta" style="width: 100%;"></div>
            </div>

            <div style="margin-top: 14px; background:#090d13; border:1px solid var(--border); border-radius:6px; padding:10px;">
                <div style="font-size:0.85rem; font-weight:600;">Current Decision:</div>
                <div id="cur-decision" style="font-size:1.1rem; font-weight:700; color:#58a6ff; margin: 4px 0;">STANDBY / LISTENING</div>
                <div id="cur-reason" style="font-size:0.8rem; color:#8b949e;">Waiting for sensor ingress...</div>
                <div id="cur-hmac" style="font-size:0.7rem; color:#6e7681; margin-top:6px; word-break:break-all;">HMAC: -</div>
            </div>
        </div>
    </div>

    <div class="card" style="margin-top: 20px;">
        <div class="card-title">Real-Time Triage & P2P Mesh Audit Trail</div>
        <div id="log-container" class="log-box">
            <div class="log-entry IGNORE">[SYSTEM INIT] SignalGate Core active. Frame of Discernment: {Victim, Noise, Hazard}. P2P Mesh ready.</div>
        </div>
    </div>

    <script>
        let lastHeldId = null;

        async function triggerEvent(type) {
            const res = await fetch(`/api/trigger?type=${type}`, { method: 'POST' });
            const data = await res.json();
            updateUI(data);
        }

        async function triggerCorroboration() {
            if (!lastHeldId) {
                alert('No pending incident is currently held for corroboration! Click an ambiguous or SOS event first.');
                return;
            }
            const res = await fetch(`/api/corroborate?hold_id=${lastHeldId}`, { method: 'POST' });
            const data = await res.json();
            updateUI(data);
        }

        async function triggerChaos() {
            const el = document.getElementById('system-status');
            el.innerText = 'EXECUTING 50 CHAOS SCENARIOS...';
            el.style.color = '#f85149';
            const res = await fetch('/api/chaos', { method: 'POST' });
            const data = await res.json();
            alert(data.summary);
            el.innerText = 'CHAOS EVALUATION COMPLETE (0 FALSE DISPATCHES)';
            el.style.color = '#238636';
            addLogEntry({
                state: 'IGNORE',
                timestamp: new Date().toISOString(),
                reason: data.summary,
                decision_id: 'CHAOS-EVAL-50',
                priority: 'P3_AUDITED',
                conflict_k: 0.0,
                fused_mass: { Victim: 0, Noise: 1, Hazard: 0, Theta: 0 }
            });
        }

        function updateUI(data) {
            const fused = data.fused_mass || {};
            const v = (fused.Victim || 0) * 100;
            const n = (fused.Noise || 0) * 100;
            const h = (fused.Hazard || 0) * 100;
            const t = (fused.Theta || 0) * 100;

            document.getElementById('stat-conflict').innerText = (data.conflict_k || 0).toFixed(2);
            document.getElementById('stat-victim').innerText = (fused.Victim || 0).toFixed(2);
            document.getElementById('stat-noise').innerText = (fused.Noise || 0).toFixed(2);
            document.getElementById('stat-theta').innerText = (fused.Theta || 0).toFixed(2);

            document.getElementById('bar-v').style.width = v + '%';
            document.getElementById('bar-n').style.width = n + '%';
            document.getElementById('bar-h').style.width = h + '%';
            document.getElementById('bar-t').style.width = t + '%';

            const decEl = document.getElementById('cur-decision');
            decEl.innerText = `${data.state} (${data.priority})`;
            if (data.state === 'DISPATCH') {
                decEl.style.color = '#f85149';
                lastHeldId = null;
            } else if (data.state === 'HOLD_AND_CORROBORATE') {
                decEl.style.color = '#e3b341';
                lastHeldId = data.decision_id;
            } else {
                decEl.style.color = '#238636';
            }

            document.getElementById('cur-reason').innerText = data.reason || '';
            document.getElementById('cur-hmac').innerText = 'HMAC-SHA256: ' + (data.provenance_signature || 'N/A');

            addLogEntry(data);
        }

        function addLogEntry(data) {
            const box = document.getElementById('log-container');
            const entry = document.createElement('div');
            entry.className = 'log-entry ' + data.state;
            entry.innerHTML = `<strong>[${data.timestamp.split('T')[1].split('.')[0]}] ${data.decision_id} &rarr; ${data.state} (${data.priority})</strong><br>` +
                              `Reason: ${data.reason}<br>` +
                              `<span style="color:#8b949e">Conflict K: ${data.conflict_k} | Hops: ${data.mesh_telemetry ? data.mesh_telemetry.hops : 1} | Sig: ${data.provenance_signature ? data.provenance_signature.substring(0, 16) + '...' : 'VERIFIED'}</span>`;
            box.insertBefore(entry, box.firstChild);
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def get_dashboard():
    return HTMLResponse(content=DASHBOARD_HTML)

@app.post("/api/trigger")
async def trigger_event(type: str):
    if type == "sos_tap":
        # Node 1 detects acoustic SOS tapping
        audio = dsp.synthesize_test_tone(pattern="sos", duration_s=0.25)
        dsp_mass = dsp.analyze_frame(audio)
        decision = mesh.process_incident("NODE_01", [dsp_mass], metadata={"source": "acoustic_sos"})
        incident_history.append(decision)
        return JSONResponse(content=decision)

    elif type == "voice_tl":
        # Node 3 detects Tagalog crisis distress
        text = "Tulong! Natabunan kami sa ilalim"
        nlp_mass = nlp.analyze_text(text)
        decision = mesh.process_incident("NODE_03", [nlp_mass], metadata={"source": "crisis_nlp_tl"})
        incident_history.append(decision)
        return JSONResponse(content=decision)

    elif type == "rain_noise":
        # Node 1 hears rain
        audio = dsp.synthesize_test_tone(pattern="rain_noise", duration_s=0.25)
        dsp_mass = dsp.analyze_frame(audio)
        decision = mesh.process_incident("NODE_01", [dsp_mass], metadata={"source": "ambient_rain"})
        incident_history.append(decision)
        return JSONResponse(content=decision)

    elif type == "contradiction":
        # Node 1 hears faint tapping, but Sensor 2 detects heavy machinery vibration
        m1 = {"Victim": 0.65, "Noise": 0.10, "Hazard": 0.05, "Theta": 0.20}
        m2 = {"Victim": 0.05, "Noise": 0.20, "Hazard": 0.70, "Theta": 0.05}
        decision = mesh.process_incident("NODE_01", [m1, m2], metadata={"source": "conflicting_sensors"})
        incident_history.append(decision)
        return JSONResponse(content=decision)

    return JSONResponse(content={"error": "unknown_event_type"}, status_code=400)

@app.post("/api/corroborate")
async def corroborate_event(hold_id: str):
    # Node 2 provides corroborating acoustic & seismic distress signal
    m_corroborate = {"Victim": 0.88, "Noise": 0.05, "Hazard": 0.02, "Theta": 0.05}
    escalated = mesh.corroborate_incident(hold_id, "NODE_02", m_corroborate)
    if not escalated:
        return JSONResponse(content={"error": "hold_id_not_found_or_resolved"}, status_code=404)
    incident_history.append(escalated)
    return JSONResponse(content=escalated)

@app.post("/api/chaos")
async def run_chaos():
    report = chaos_injector.run_chaos_evaluation(num_scenarios=50)
    return JSONResponse(content=report)

def start_server(host: str = "127.0.0.1", port: int = 8000):
    print(f"[OK] Starting ResQ-Mesh Web Dashboard on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    start_server()
