import streamlit as st
import pandas as pd
from PIL import Image
from core.config import SystemConfig
from core.engine import AIEngine
from core.forensics import ForensicToolkit

# --- 1. PAGE SETUP ---
st.set_page_config(
    page_title="PhishGuard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Intelligence Engine
engine = AIEngine()

# --- 2. SESSION STATE MANAGEMENT ---
# We store data here so it doesn't disappear when you click buttons
if 'scan_result' not in st.session_state: st.session_state.scan_result = ""
if 'arena_a' not in st.session_state: st.session_state.arena_a = ""
if 'arena_b' not in st.session_state: st.session_state.arena_b = ""
if 'headers' not in st.session_state: st.session_state.headers = {}
if 'geo_data' not in st.session_state: st.session_state.geo_data = pd.DataFrame()

# --- 3. CUSTOM STYLING (CSS) ---
st.markdown("""
<style>
    /* Dark Theme Optimization */
    .main { background-color: #0E1117; }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; color: #E6EDF3; }
    
    /* Card Containers */
    .stCard {
        background-color: #161B22;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #30363D;
        margin-bottom: 20px;
    }
    
    /* Report Box Styling */
    .report-box {
        background-color: #0d1117;
        border: 1px solid #238636; /* Green border for verified output */
        border-radius: 6px;
        padding: 20px;
        margin-top: 10px;
    }
    
    /* Map Container */
    .map-container {
        border: 1px solid #30363D;
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2092/2092663.png", width=50)
    st.title("PhishGuard")
    st.caption("v3.0 | Forensic Suite")
    
    st.markdown("---")
    st.markdown("### 🧭 Navigation Module")
    
    page_selection = st.radio(
        "Select Workspace:",
        ["Forensic Scan (Single)", "Model Arena (Compare)"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.success("✅ Core Engine: **ONLINE**")
    if SystemConfig.GOOGLE_API_KEY:
        st.success("✅ Cloud API: **CONNECTED**")
    else:
        st.warning("⚠️ Cloud API: **OFFLINE**")

# ==================================================
# PAGE 1: SINGLE FORENSIC SCAN
# ==================================================
if page_selection == "Forensic Scan (Single)":
    st.title("🔍 Single Artifact Analysis")
    st.markdown("Deep-dive forensic scanning with Geo-Location tracing.")
    
    # Layout: Input (Left) | Dashboard (Right)
    col_input, col_dash = st.columns([1, 2], gap="large")
    
    # --- LEFT COLUMN: INPUT ---
    with col_input:
        st.subheader("1. Input & Config")
        
        # Model Selector
        model_choice = st.selectbox("Inference Model", list(SystemConfig.MODELS.keys()))
        
        # Tabs
        tab_eml, tab_img = st.tabs(["📧 Email (.eml)", "📸 Screenshot"])
        
        parsed_text = ""
        uploaded_img = None
        
        with tab_eml:
            u_eml = st.file_uploader("Upload File", type=['eml'], key="single_eml")
            if u_eml:
                # INSTANT ACTION: Parse & Map immediately
                st.session_state.headers, parsed_text = ForensicToolkit.parse_eml(u_eml)
                
                # Generate Map Data
                raw_str = str(st.session_state.headers)
                ips = ForensicToolkit.extract_ips(raw_str)
                st.session_state.geo_data = ForensicToolkit.get_geo_dataframe(ips)
                
                st.info(f"Loaded: {st.session_state.headers.get('Subject', 'Unknown')}")

        with tab_img:
            u_img = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'], key="single_img")
            if u_img:
                uploaded_img = Image.open(u_img)
                st.image(uploaded_img, caption="Evidence Preview", use_container_width=True)

        # Scan Button
        st.divider()
        if st.button("🚀 Initialize Scan", type="primary", use_container_width=True):
            if not parsed_text and not uploaded_img:
                st.error("Evidence required.")
            else:
                with st.spinner("AI is thinking... (Analyzing Vectors)"):
                    st.session_state.scan_result = engine.analyze(
                        model_key=model_choice,
                        text_data=parsed_text,
                        image_data=uploaded_img,
                        mode="SINGLE"
                    )

    # --- RIGHT COLUMN: DASHBOARD ---
    with col_dash:
        st.subheader("2. Forensic Dashboard")
        
        # FEATURE A: HEADER VIEWER (Immediate)
        if st.session_state.headers:
            with st.expander("📄 Header Metadata Viewer", expanded=False):
                st.json(st.session_state.headers)

        # FEATURE B: LOCATION MAP (Immediate)
        if not st.session_state.geo_data.empty:
            st.markdown("**🌍 Network Topology (IP Trace)**")
            st.markdown('<div class="map-container">', unsafe_allow_html=True)
            st.map(st.session_state.geo_data, zoom=1, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            with st.expander("View IP Routing Table"):
                st.dataframe(st.session_state.geo_data[["IP Address", "Location Context"]], hide_index=True)

        # FEATURE C: AI REPORT (After Scan)
        if st.session_state.scan_result:
            st.markdown("### 🛡️ AI Forensic Report")
            st.markdown('<div class="report-box">', unsafe_allow_html=True)
            st.markdown(st.session_state.scan_result)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Export
            pdf_bytes = ForensicToolkit.generate_pdf(
                "Single Scan", 
                st.session_state.headers, 
                st.session_state.scan_result
            )
            st.download_button("⬇️ Download PDF Report", pdf_bytes, "forensic_report.pdf", "application/pdf")

# ==================================================
# PAGE 2: MODEL ARENA (COMPARISON)
# ==================================================
elif page_selection == "Model Arena (Compare)":
    st.title("⚔️ Model Arena")
    st.markdown("Compare two AI models side-by-side to validate findings.")
    
    # 1. Shared Evidence Input
    with st.container():
        st.subheader("1. Shared Evidence")
        c1, c2 = st.columns([1, 3])
        
        with c1:
            u_arena = st.file_uploader("Upload Artifact", type=['eml', 'png', 'jpg'], key="arena_up")
        
        arena_text = ""
        arena_img = None
        
        with c2:
            if u_arena:
                # Determine type
                if u_arena.name.endswith('.eml'):
                    h, b = ForensicToolkit.parse_eml(u_arena)
                    arena_text = f"HEADERS: {h}\nBODY: {b[:2000]}"
                    st.success(f"📧 Loaded Email: {h.get('Subject')}")
                    # Show Map here too for consistency
                    ips = ForensicToolkit.extract_ips(str(h))
                    if ips:
                        st.info(f"🌍 {len(ips)} IP Hops extracted ready for analysis.")
                else:
                    arena_img = Image.open(u_arena)
                    st.image(arena_img, width=150, caption="Visual Evidence")
            else:
                st.info("Waiting for upload...")

    st.divider()

    # 2. Contender Selection
    st.subheader("2. Select Contenders")
    col_a, col_b = st.columns(2)
    
    with col_a:
        mod_a = st.selectbox("Model A (Left)", list(SystemConfig.MODELS.keys()), index=1)
    with col_b:
        mod_b = st.selectbox("Model B (Right)", list(SystemConfig.MODELS.keys()), index=2)

    if st.button("⚔️ Run Comparative Analysis", type="primary", use_container_width=True):
        if not arena_text and not arena_img:
            st.error("Upload evidence first.")
        else:
            with st.spinner("Running parallel inference protocols..."):
                st.session_state.arena_a = engine.analyze(mod_a, arena_text, arena_img, mode="COMPARE")
                st.session_state.arena_b = engine.analyze(mod_b, arena_text, arena_img, mode="COMPARE")
                st.success("Comparison Complete!")

    # 3. Results
    if st.session_state.arena_a and st.session_state.arena_b:
        r1, r2 = st.columns(2)
        with r1:
            st.markdown(f"### 🤖 {mod_a}")
            st.markdown('<div class="report-box">', unsafe_allow_html=True)
            st.markdown(st.session_state.arena_a)
            st.markdown('</div>', unsafe_allow_html=True)
        with r2:
            st.markdown(f"### 🤖 {mod_b}")
            st.markdown('<div class="report-box">', unsafe_allow_html=True)
            st.markdown(st.session_state.arena_b)
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Comparison Export
        st.divider()
        pdf_bytes = ForensicToolkit.generate_pdf(
            "Model Comparison",
            {}, # No headers needed for this summary
            f"MODEL A ({mod_a}):\n{st.session_state.arena_a}",
            f"MODEL B ({mod_b}):\n{st.session_state.arena_b}"
        )
        st.download_button("⬇️ Download Comparison PDF", pdf_bytes, "comparison_report.pdf", "application/pdf")