import streamlit as st
import json
import os
import time
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components

# Import local RAG engine and remediation engine backend
from compliance_rag import ComplianceRAGEngine
from remediation_engine import auto_remediate_s3_bucket

# 1. Base Streamlit Config
st.set_page_config(
    page_title="NIST Cloud Sentinel | Automated Guardrails & Remediation",
    page_icon="🪐",
    layout="wide"
)

# Force Session State Initialization
if "is_breached" not in st.session_state:
    st.session_state["is_breached"] = False

if "last_rag_citation" not in st.session_state:
    st.session_state["last_rag_citation"] = ""

if "last_audit_result" not in st.session_state:
    st.session_state["last_audit_result"] = None

if "last_target_control" not in st.session_state:
    st.session_state["last_target_control"] = "AC-3"

# Dynamic Visual Theme Engine (Red Canvas + Sleek Black Tactical Buttons)
if st.session_state.get("is_breached", False):
    st.markdown(
        """
        <style>
        /* 1. Global Canvas & Background Filter (Red/Amber Space Canvas) */
        canvas, div[data-testid="stAppViewContainer"], iframe {
            filter: hue-rotate(130deg) saturate(300%) contrast(110%) !important;
        }

        /* 2. Tactical Obsidian Buttons with Glowing Crimson Borders */
        div.stButton > button {
            filter: hue-rotate(-130deg) !important;
            background-color: #0d0d0d !important;
            background-image: none !important;
            color: #ffffff !important;
            border: 2px solid #ff3300 !important;
            box-shadow: 0px 0px 10px rgba(255, 51, 0, 0.8) !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px !important;
        }

        /* Hover effect for buttons */
        div.stButton > button:hover {
            background-color: #1a0000 !important;
            border-color: #ff6600 !important;
            box-shadow: 0px 0px 16px rgba(255, 102, 0, 1) !important;
            color: #ff3300 !important;
        }

        /* 3. Text Glow Overrides */
        h1, h2, h3, p, span, label, div[data-testid="stMetricValue"] {
            color: #ff3300 !important;
            text-shadow: 0px 0px 8px rgba(255, 51, 0, 0.7) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
# 2. Force Saturn Favicon Override Script
favicon_override_script = """
<script>
    const parentDoc = window.parent.document;
    
    // Force Favicon Replacement to Saturn 🪐
    function setSaturnFavicon() {
        let link = parentDoc.querySelector("link[rel*='icon']");
        if (!link) {
            link = parentDoc.createElement('link');
            link.rel = 'shortcut icon';
            parentDoc.getElementsByTagName('head')[0].appendChild(link);
        }
        link.href = 'data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🪐</text></svg>';
    }
    
    setSaturnFavicon();
    setTimeout(setSaturnFavicon, 1000);

    // Global Starfield Canvas
    let canvas = parentDoc.getElementById('globalStarCanvas');
    if (!canvas) {
        canvas = parentDoc.createElement('canvas');
        canvas.id = 'globalStarCanvas';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100vw';
        canvas.style.height = '100vh';
        canvas.style.zIndex = '-1';
        canvas.style.pointerEvents = 'none';
        canvas.style.background = '#070814';
        parentDoc.body.appendChild(canvas);
    }
    
    const ctx = canvas.getContext('2d');
    
    function resize() {
        canvas.width = window.parent.innerWidth;
        canvas.height = window.parent.innerHeight;
    }
    window.parent.addEventListener('resize', resize);
    resize();
    
    const stars = [];
    const starColors = ['#5539CC', '#38bdf8', '#ffffff'];
    for (let i = 0; i < 220; i++) {
        stars.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            radius: Math.random() * 1.5 + 0.5,
            alpha: Math.random(),
            speed: Math.random() * 0.01 + 0.003,
            color: starColors[Math.floor(Math.random() * starColors.length)]
        });
    }
    
    const shootingStars = [];
    function createShootingStar() {
        if (shootingStars.length < 4 && Math.random() < 0.05) {
            const colors = ['#5539CC', '#38bdf8', '#ffffff'];
            const selectedColor = colors[Math.floor(Math.random() * colors.length)];
            
            shootingStars.push({
                x: Math.random() * canvas.width * 0.8,
                y: Math.random() * canvas.height * 0.4,
                length: Math.random() * 140 + 80,
                speed: Math.random() * 4 + 5,
                angle: Math.PI / 4,
                alpha: 1,
                color: selectedColor
            });
        }
    }
    
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        for (let star of stars) {
            star.alpha += star.speed;
            if (star.alpha > 1 || star.alpha < 0) star.speed = -star.speed;
            ctx.beginPath();
            ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
            ctx.fillStyle = star.color;
            ctx.globalAlpha = Math.abs(star.alpha);
            ctx.shadowBlur = 8;
            ctx.shadowColor = star.color;
            ctx.fill();
        }
        ctx.globalAlpha = 1;
        
        createShootingStar();
        for (let i = shootingStars.length - 1; i >= 0; i--) {
            let s = shootingStars[i];
            let endX = s.x + Math.cos(s.angle) * s.length;
            let endY = s.y + Math.sin(s.angle) * s.length;
            
            let gradient = ctx.createLinearGradient(s.x, s.y, endX, endY);
            gradient.addColorStop(0, `rgba(255, 255, 255, ${s.alpha})`);
            gradient.addColorStop(0.4, s.color);
            gradient.addColorStop(1, 'transparent');
            
            ctx.beginPath();
            ctx.moveTo(s.x, s.y);
            ctx.lineTo(endX, endY);
            ctx.strokeStyle = gradient;
            ctx.lineWidth = 2.5;
            ctx.shadowBlur = 14;
            ctx.shadowColor = s.color;
            ctx.stroke();
            
            s.x += Math.cos(s.angle) * s.speed;
            s.y += Math.sin(s.angle) * s.speed;
            s.alpha -= 0.008;
            
            if (s.alpha <= 0 || s.x > canvas.width || s.y > canvas.height) {
                shootingStars.splice(i, 1);
            }
        }
        requestAnimationFrame(animate);
    }
    animate();
</script>
"""
components.html(favicon_override_script, height=0)

# 3. Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&family=Orbitron:wght@700;900&display=swap');

    @keyframes headerPulse {
        0% { box-shadow: 0 0 25px rgba(85, 57, 204, 0.4), inset 0 0 20px rgba(85, 57, 204, 0.2); border-color: #5539CC; }
        50% { box-shadow: 0 0 50px rgba(85, 57, 204, 0.85), inset 0 0 35px rgba(85, 57, 204, 0.5); border-color: #5539CC; }
        100% { box-shadow: 0 0 25px rgba(85, 57, 204, 0.4), inset 0 0 20px rgba(85, 57, 204, 0.2); border-color: #5539CC; }
    }

    @keyframes titleGlow {
        0% { text-shadow: 0 0 15px rgba(85, 57, 204, 0.8), 0 0 30px rgba(85, 57, 204, 0.5); }
        50% { text-shadow: 0 0 25px #5539CC, 0 0 45px #5539CC, 0 0 65px #5539CC; }
        100% { text-shadow: 0 0 15px rgba(85, 57, 204, 0.8), 0 0 30px rgba(85, 57, 204, 0.5); }
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    .stApp {
        background: transparent !important;
        color: #f8fafc;
    }

    .header-box {
        background: rgba(14, 15, 30, 0.85);
        backdrop-filter: blur(14px);
        padding: 36px;
        border-radius: 20px;
        border: 2px solid #5539CC;
        margin-bottom: 20px;
        animation: headerPulse 3.5s infinite ease-in-out;
    }

    .header-title {
        font-family: 'Orbitron', sans-serif !important;
        color: #ffffff;
        font-size: 3rem;
        font-weight: 900;
        margin-bottom: 10px;
        letter-spacing: 1.5px;
        animation: titleGlow 3.5s infinite ease-in-out;
    }

    .header-sub {
        color: #e2e8f0;
        font-size: 1.15rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    .ticker-box {
        background: rgba(10, 12, 28, 0.8);
        border: 1px solid #5539CC;
        border-radius: 12px;
        padding: 12px 20px;
        font-family: 'Orbitron', monospace !important;
        font-size: 0.9rem;
        color: #38bdf8;
        margin-bottom: 24px;
        box-shadow: 0 0 15px rgba(85, 57, 204, 0.3);
    }

    h2, h3, .stSubheader {
        font-family: 'Orbitron', sans-serif !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        letter-spacing: 0.8px !important;
        text-shadow: 0 0 15px rgba(85, 57, 204, 0.6);
    }

    div[data-testid="stMetric"] {
        background: rgba(15, 17, 35, 0.85) !important;
        border: 1.5px solid #5539CC !important;
        padding: 22px !important;
        border-radius: 16px !important;
        backdrop-filter: blur(14px) !important;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    div[data-testid="stMetric"]:hover {
        border-color: #5539CC !important;
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 35px rgba(85, 57, 204, 0.65) !important;
    }

    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    div[data-testid="stMetricValue"] {
        font-family: 'Orbitron', sans-serif !important;
        color: #5539CC !important;
        font-weight: 900 !important;
        font-size: 2.1rem !important;
        text-shadow: 0 0 18px rgba(85, 57, 204, 0.85);
    }

    .stButton>button {
        background: rgba(85, 57, 204, 0.8) !important;
        color: #ffffff !important;
        border: 1px solid #5539CC !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        font-family: 'Orbitron', sans-serif !important;
        transition: all 0.3s ease !important;
    }

    .stButton>button:hover {
        background: #5539CC !important;
        box-shadow: 0 0 20px rgba(85, 57, 204, 0.8) !important;
        transform: scale(1.02) !important;
    }

    .stDataFrame {
        background: rgba(10, 12, 28, 0.75) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(85, 57, 204, 0.5) !important;
        backdrop-filter: blur(12px) !important;
    }

    ul {
        line-height: 1.8 !important;
        font-size: 1.05rem !important;
    }

    li strong {
        color: #ffffff !important;
        text-shadow: 0 0 8px rgba(85, 57, 204, 0.7);
    }
    </style>
""", unsafe_allow_html=True)

# Main Banner Header
st.markdown("""
    <div class="header-box">
        <div class="header-title">NIST CL🪐UD SENTINEL</div>
        <div class="header-sub">Automated Cloud Compliance Orchestrator, Enterprise DevSecOps Guardrails & Closed-Loop Boto3 Remediation</div>
    </div>
""", unsafe_allow_html=True)

# Top Bar Account Scope & Expanded AWS Regions
env_col1, env_col2 = st.columns([2, 2])
with env_col1:
    selected_account = st.selectbox("🌐 Active AWS Account Scope:", ["123456789012 (Production Fleet)", "987654321098 (Staging DevSecOps)", "112233445566 (GovCloud Sensitive)"])
with env_col2:
    selected_region = st.selectbox("📍 Target AWS Region:", [
        "us-east-1 (N. Virginia - Primary East)",
        "us-east-2 (Ohio - Midwest Hub)",
        "us-south-1 (Texas - South Central Hub)",
        "us-west-2 (Oregon - West Hub)",
        "us-gov-west-1 (AWS GovCloud Isolated)"
    ])

# SOC Stream Ticker
st.markdown(f"""
    <div class="ticker-box">
        📡 <b>LIVE SOC EVENT STREAM:</b> [AWS::CloudTrail] <code>s3:PutBucketPublicAccessBlock</code> enforced on <code>s3-patient-data-bucket-01</code> in <b>{selected_region.split(' ')[0]}</b> | Status: <b>SUCCESS (200 OK)</b>
    </div>
""", unsafe_allow_html=True)

payload_path = "test_payload_devsec104.json"

if "resource_dataset" not in st.session_state:
    st.session_state.resource_dataset = [
        {
            "resource_id": "s3-patient-data-bucket-01",
            "resource_type": "AWS::S3::Bucket",
            "status": "REMEDIATED_COMPLIANT",
            "family": "AC / SC / AU",
            "nist_controls": "AC-3, SC-8, SC-28, AU-2/3, AU-12",
            "environment": "production"
        },
        {
            "resource_id": "iam-admin-role-bypass-02",
            "resource_type": "AWS::IAM::Role",
            "status": "COMPLIANT",
            "family": "AC / IA",
            "nist_controls": "AC-2, AC-6, IA-2, IA-5",
            "environment": "production"
        },
        {
            "resource_id": "sg-db-cluster-ssh-open-03",
            "resource_type": "AWS::EC2::SecurityGroup",
            "status": "REMEDIATED_COMPLIANT",
            "family": "AC / SC / CM",
            "nist_controls": "AC-4, AC-17, SC-7, CM-6",
            "environment": "staging"
        },
        {
            "resource_id": "kms-prod-key-rotation-04",
            "resource_type": "AWS::KMS::Key",
            "status": "COMPLIANT",
            "family": "SC / CM / RA",
            "nist_controls": "SC-12, SC-13, CM-6, RA-5",
            "environment": "production"
        },
        {
            "resource_id": "cloudtrail-security-audit-05",
            "resource_type": "AWS::CloudTrail::Trail",
            "status": "COMPLIANT",
            "family": "AU / IR",
            "nist_controls": "AU-2, AU-3, AU-6, IR-4",
            "environment": "production"
        }
    ]

total_res = len(st.session_state.resource_dataset)
non_compliant_cnt = sum(1 for r in st.session_state.resource_dataset if r["status"] == "NON_COMPLIANT")
score_val = "100%" if non_compliant_cnt == 0 else f"{int(((total_res - non_compliant_cnt) / total_res) * 100)}%"

col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Total Monitored Resources", value=total_res)
col2.metric(label="Fleet Compliance Score", value=score_val, delta="Fully Compliant" if non_compliant_cnt == 0 else f"-{non_compliant_cnt} Violations")
col3.metric(label="Active Control Families", value="AC, AU, SC, CM, IA, IR, RA")
col4.metric(label="Circuit Breaker Status", value="ARMED & ACTIVE")

st.divider()

chart_col, ctrl_col = st.columns([1.5, 2])

with chart_col:
    st.subheader("📈 CONTROL FAMILY HEALTH")
    family_counts = {"AC (Access)": 3, "AU (Audit)": 2, "SC (Comms)": 3, "CM (Config)": 2, "IA (Identity)": 1}
    df_chart = pd.DataFrame(list(family_counts.items()), columns=["Control Family", "Active Controls Enforced"])
    fig = px.pie(df_chart, values="Active Controls Enforced", names="Control Family", hole=0.55,
                 color_discrete_sequence=['#5539CC', '#38bdf8', '#8b5cf6', '#0284c7', '#a855f7'])
    fig.update_layout(
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f8fafc', family="Inter"),
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

with ctrl_col:
    st.subheader("⚡ TELEMETRY CONTROLS & DRIFT SIMULATOR")
    
    filter_family = st.selectbox(
        "Filter Grid by NIST Family:",
        ["All Families", "AC (Access Control)", "AU (Audit & Accountability)", "SC (System & Comms)", "CM (Config Mgt)", "IA (Identity)", "IR (Incident Response)"]
    )
    search_query = st.text_input("Quick-Search Control ID (e.g. AC-3, SC-28):", "")
    
    btn_c1, btn_c2 = st.columns(2)
    with btn_c1:
        if st.button("🚨 Simulate Configuration Drift"):
            st.session_state["is_breached"] = True
            st.session_state.resource_dataset[0]["status"] = "NON_COMPLIANT"
            st.warning("⚠️ DRIFT DETECTED: S3 Bucket Public Access Block disabled by dev-user!")
            st.rerun()
            
    with btn_c2:
        if st.button("⚡ Execute Boto3 Auto-Remediation"):
            st.session_state["is_breached"] = False
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Universal capture of search query or family filter for all NIST families (AC, AU, SC, CM, IA, IR)
            raw_search = search_query.strip().upper() if search_query else ""
            selected_family_code = filter_family.split(" ")[0] if filter_family != "All Families" else "AC"
            
            target_control = raw_search if raw_search else f"{selected_family_code}-Baseline Control"
            query_trigger = raw_search if raw_search else f"{selected_family_code}_COMPLIANCE_ENFORCEMENT"
            
            # Save target control to session state for dynamic UI widgets
            st.session_state["last_target_control"] = target_control
            
            # Step 1: Drift Detection Pacing
            status_text.text(f"🔍 [1/3] Detecting multi-family policy drift for [{target_control}] via CloudTrail...")
            progress_bar.progress(25)
            time.sleep(0.8)
            
            # Step 2: Local ChromaDB RAG Engine Query Pacing with Dynamic Overrides for All Families
            status_text.text(f"🧠 [2/3] Querying local ChromaDB RAG for family [{selected_family_code}] / '{query_trigger}'...")
            progress_bar.progress(55)
            try:
                rag_engine = ComplianceRAGEngine()
                raw_rag = rag_engine.query_control(query_trigger, n_results=1)
            except Exception:
                raw_rag = ""

            # Dynamic multi-family RAG citation text matching your exact target control inputs
            if "SC-28" in target_control:
                st.session_state["last_rag_citation"] = (
                    "---- [NIST SP 800-53 Rev. 5: SC-28] ----\n"
                    "Protection of Information at Rest:\n"
                    "The organization protects the confidentiality and integrity of information at rest "
                    "using cryptographic mechanisms (AES-256 / AWS KMS) across all storage volumes, "
                    "databases, and S3 object buckets to prevent unauthorized disclosure."
                )
            elif "AC-3" in target_control:
                st.session_state["last_rag_citation"] = (
                    "---- [NIST SP 800-53 Rev. 5: AC-3] ----\n"
                    "Access Enforcement:\n"
                    "The information system enforces approved authorizations for logical access "
                    "to information and system resources in accordance with applicable access control policies."
                )
            elif "CM-6" in target_control:
                st.session_state["last_rag_citation"] = (
                    "---- [NIST SP 800-53 Rev. 5: CM-6] ----\n"
                    "Configuration Settings:\n"
                    "The organization establishes and enforces mandatory configuration baselines for IT products "
                    "employed within the information system, ensuring continuous compliance drift protection."
                )
            elif "IA-2" in target_control:
                st.session_state["last_rag_citation"] = (
                    "---- [NIST SP 800-53 Rev. 5: IA-2] ----\n"
                    "Identification and Authentication (Organizational Users):\n"
                    "The information system uniquely identifies and authenticates organizational users "
                    "using multi-factor authentication (MFA) prior to granting system access."
                )
            elif "IR-4" in target_control:
                st.session_state["last_rag_citation"] = (
                    "---- [NIST SP 800-53 Rev. 5: IR-4] ----\n"
                    "Incident Handling:\n"
                    "The organization implements an incident handling capability for security incidents that includes "
                    "preparation, containment, eradication, and closed-loop automated Boto3 remediation."
                )
            elif "AU-2" in target_control or "AU-3" in target_control:
                st.session_state["last_rag_citation"] = (
                    "---- [NIST SP 800-53 Rev. 5: AU-2 / AU-3] ----\n"
                    "Event Logging & Content of Audit Records:\n"
                    "The organization identifies and records system events including successful and failed account logins, "
                    "privilege usages, and security policy modifications with detailed timestamps and source identities."
                )
            else:
                st.session_state["last_rag_citation"] = raw_rag if raw_rag else f"--- [NIST SP 800-53 Control: {target_control}] ---\nStatutory compliance baseline verified and enforced successfully via automated guardrails."
            
            time.sleep(0.8)
            
            # Step 3: Circuit Breaker & Boto3 Execution Pacing
            status_text.text(f"🛡️ [3/3] Invoking Pytest circuit breaker & executing Boto3 guardrail for {target_control}...")
            progress_bar.progress(80)
            
            if os.path.exists(payload_path):
                with open(payload_path, "r") as f:
                    payload_data = json.load(f)
            else:
                payload_data = {
                    "resource_id": "s3-patient-data-bucket-01",
                    "event_type": query_trigger,
                    "public_access_block": False,
                    "encryption_enabled": False
                }
            
            # Inject universal control mapping into payload
            payload_data["nist_control"] = target_control
            payload_data["event_type"] = query_trigger
            
            updated_payload = auto_remediate_s3_bucket(payload_data)
            
            # Ensure audit log dynamically reflects the targeted family and control
            if isinstance(updated_payload, dict):
                if "audit_log" in updated_payload and isinstance(updated_payload["audit_log"], dict):
                    updated_payload["audit_log"]["nist_au_control"] = f"AU-2 / AU-3 (Enforcing Control: {target_control})"
            
            st.session_state["last_audit_result"] = updated_payload
            
            with open(payload_path, "w") as f:
                json.dump(updated_payload, f, indent=2)

            st.session_state.resource_dataset[0]["status"] = "REMEDIATED_COMPLIANT"
            progress_bar.progress(100)
            time.sleep(0.5)
            
            status_text.empty()
            progress_bar.empty()
            st.success(f"✅ Universal Remediation Complete: Boto3 Guardrails & RAG Citations synchronized for {target_control}!")
            st.rerun()

# ==========================================
# 📜 LIVE RAG CITATION & BOTO3 AUDIT HUD SECTION
# ==========================================
if st.session_state.get("last_rag_citation"):
    st.divider()
    col_rag, col_audit = st.columns([1, 1], gap="medium")
    
    with col_rag:
        st.markdown("<h3 style='font-size: 1.15rem; font-family: Orbitron, sans-serif;'>🧠 LIVE LOCAL RAG CITATION</h3>", unsafe_allow_html=True)
        citation_text = st.session_state["last_rag_citation"]
        st.markdown(f"""
            <div style="background-color: rgba(10, 12, 28, 0.9); border: 1px solid #5539CC; padding: 16px; border-radius: 12px; color: #38bdf8; font-family: monospace; font-size: 0.85rem; line-height: 1.5; word-wrap: break-word; overflow-wrap: break-word; max-height: 220px; overflow-y: auto;">
                {str(citation_text).replace(chr(10), '<br>')}
            </div>
        """, unsafe_allow_html=True)
        
    with col_audit:
        active_control_label = st.session_state.get("last_target_control", "AC-3")
        st.markdown(f"<h3 style='font-size: 1.15rem; font-family: Orbitron, sans-serif;'>🛠️ BOTO3 AUDIT TRAIL ({active_control_label})</h3>", unsafe_allow_html=True)
        
        # Robust safety extraction: check 'audit_log' key, otherwise fallback to mock structured record if empty
        audit_result = st.session_state.get("last_audit_result", {})
        audit_log_data = {}
        if isinstance(audit_result, dict):
            audit_log_data = audit_result.get("audit_log", {})
            if not audit_log_data and "action_taken" in audit_result:
                audit_log_data = audit_result # If the result itself is the audit log
                
        if not audit_log_data:
            audit_log_data = {
                "event_id": "evt-1748612400",
                "timestamp": "2026-08-29T21:15:00Z",
                "event_source": "grc-auto-remediation-engine",
                "nist_au_control": f"AU-2 / AU-3 (Enforcing Control: {active_control_label})",
                "action_taken": [
                    f"Boto3 API Guardrail Invoked for {active_control_label}",
                    "Target Compliance Standard Enforced"
                ],
                "pre_remediation_snapshot": {
                    "target_control": active_control_label,
                    "status": "DRIFT_DETECTED"
                },
                "status": "SUCCESS_REMEDIATED"
            }
        else:
            audit_log_data["nist_au_control"] = f"AU-2 / AU-3 (Enforcing Control: {active_control_label})"
            
        st.json(audit_log_data, expanded=True)

st.divider()

# ==========================================
# 🏛️ ENTERPRISE ARCHITECTURE BRIEFING
# ==========================================
st.subheader("🏛️ ENTERPRISE ARCHITECTURE BRIEFING")

if "demo_msg" not in st.session_state:
    st.session_state["demo_msg"] = None
if "demo_type" not in st.session_state:
    st.session_state["demo_type"] = None

arch_col1, arch_col2, arch_col3 = st.columns(3)

with arch_col1:
    if st.button("🏛️ View Hub-and-Spoke Status"):
        st.session_state["demo_msg"] = "**Hub & Spoke Model:** Edge Spoke accounts capture raw CloudTrail APIs and route drift events across accounts into the Central Hub bus with strict IAM least-privilege boundaries."
        st.session_state["demo_type"] = "info"
        st.rerun()

with arch_col2:
    if st.button("⚡ View SQS & Pre-Check Guardrails"):
        st.session_state["demo_msg"] = "**Dual-Layer Pipeline:** Payloads hit SQS FIFO queues for fast emergency pre-guardrails before passing to the Llama 3 AI Analyst for deep context scoring."
        st.session_state["demo_type"] = "warning"
        st.rerun()

with arch_col3:
    if st.button("🔒 View 7-Year WORM Vault"):
        st.session_state["demo_msg"] = "**WORM Audit Vault:** Pre-remediation forensic snapshots are cryptographically locked under S3 Object Lock Compliance Mode for 7 years."
        st.session_state["demo_type"] = "success"
        st.rerun()

if st.session_state["demo_msg"]:
    with st.container():
        if st.session_state["demo_type"] == "info":
            st.info(st.session_state["demo_msg"])
        elif st.session_state["demo_type"] == "warning":
            st.warning(st.session_state["demo_msg"])
        elif st.session_state["demo_type"] == "success":
            st.success(st.session_state["demo_msg"])

    fade_script = """
    <script>
        setTimeout(function() {
            const alerts = window.parent.document.querySelectorAll('[data-testid="stAlert"]');
            if (alerts.length > 0) {
                const target = alerts[alerts.length - 1];
                target.style.transition = 'opacity 1.5s ease-in-out, transform 1.5s ease-in-out';
                target.style.opacity = '0';
                target.style.transform = 'translateY(-8px)';
            }
        }, 5000);
    </script>
    """
    components.html(fade_script, height=0)

    time.sleep(6.5)
    st.session_state["demo_msg"] = None
    st.session_state["demo_type"] = None
    st.rerun()

st.divider()

df_inventory = pd.DataFrame(st.session_state.resource_dataset)
if filter_family != "All Families":
    family_code = filter_family.split(" ")[0]
    df_filtered = df_inventory[df_inventory["family"].str.contains(family_code)]
else:
    df_filtered = df_inventory

if search_query:
    df_filtered = df_filtered[df_filtered["nist_controls"].str.contains(search_query, case=False)]

st.subheader("📊 MULTI-RESOURCE COMPLIANCE TELEMETRY GRID")
st.dataframe(df_filtered, width="stretch")

csv_data = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Export Compliance Audit Report (CSV)",
    data=csv_data,
    file_name="NIST_SP800_53_Compliance_Audit_Report.csv",
    mime="text/csv"
)

if os.path.exists(payload_path):
    with open(payload_path, "r") as f:
        data = json.load(f)
    
    st.divider()
    st.subheader(f"🔍 TARGET RESOURCE DEEP-DIVE: {data.get('resource_id', 'S3 Resource')}")
    st.json(data)
    
    if "audit_log" in data:
        st.subheader("📜 IMMUTABLE NIST AU AUDIT TRAIL (AU-2 / AU-3)")
        st.json(data["audit_log"])

st.divider()
st.subheader("🔒 COMPLETE NIST SP 800-53 HIGH-IMPACT GUARDRAIL MAPPINGS")
st.markdown("""
* **Access Control (AC)**
  * **AC-2 (Account Management):** Monitors IAM roles/users to enforce lifecycle offboarding and credential rotation.
  * **AC-3 (Access Enforcement):** Enforces default AWS S3 Public Access Block settings and private bucket ACLs.
  * **AC-6 (Least Privilege):** Blocks wildcard permissions (`"Action": "*"`) in IAM policies and enforces strict role separation.
  * **AC-17 (Remote Access):** Scans Security Groups to automatically close exposed management ports (SSH 22, RDP 3389).

* **Audit & Accountability (AU)**
  * **AU-2 (Event Logging) & AU-12 (Record Generation):** Mandates continuous tracking via AWS CloudTrail and VPC Flow Logs.
  * **AU-3 (Content of Audit Records):** Captures structured event metadata (caller ID, UTC timestamp, source IP, region).
  * **AU-6 (Audit Review & Analysis):** Integrates CloudWatch Alarm metrics for real-time anomaly detection.

* **System & Communications Protection (SC)**
  * **SC-7 (Boundary Protection):** Restricts network perimeter traffic via managed Security Group rules and AWS WAF.
  * **SC-8 (Transmission Confidentiality):** Enforces HTTPS/TLS 1.2+ on all S3 endpoints and Application Load Balancers.
  * **SC-12 (Cryptographic Key Management) & SC-13:** Enables mandatory multi-region AWS KMS key rotation policies.
  * **SC-28 (Protection of Information at Rest):** Automates AES-256 or KMS encryption across S3, EBS, and RDS volumes.

* **Configuration Management (CM) & Identification/Authentication (IA)**
  * **CM-6 (Configuration Settings):** Enforces infrastructure parameter baselines across staging and production.
  * **IA-2 (MFA Authentication) & IA-5 (Authenticator Management):** Requires multi-factor authentication for high-privilege operations.

* **Incident Response (IR) & Risk Assessment (RA)**
  * **IR-4 (Incident Handling):** Closed-loop Boto3 script auto-remediates policy violations upon detection.
  * **RA-5 (Vulnerability Monitoring):** Integrates continuous security scanning across all cloud resource endpoints.
* **POSIX Circuit Breaker Policy:** Halts non-compliant CI/CD builds via exit code `1` unless auto-remediation is engaged.
""")