"""ScamShield — simplified SMS scam detection demo.

Run from the project root:
    streamlit run app.py

Expected project modules:
    config.py
    src/rag.py
    src/explain.py
    src/robustness.py
"""

import html
import random

import joblib
import pandas as pd
import streamlit as st

import config
from src.rag import Retriever
from src.explain import explain
from src.robustness import ATTACKS


st.set_page_config(
    page_title="ScamShield",
    page_icon="🛡",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------------------------
# WINDOWS XP × NEO-BRUTALIST DESIGN SYSTEM
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    :root {
        --canvas:#08090B; --panel:#101216; --panel-raised:#15181E;
        --line:#30343B; --ink:#F4F5F7; --muted:#A2A8B2;
        --red:#F04452; --red-soft:#2A1115;
        --green:#39D98A; --green-soft:#10251B;
        --amber:#F5BE45; --amber-soft:#30240D;
    }
    html, body, [class*="css"] { font-family:'Space Grotesk',sans-serif; }
    .stApp { background:var(--canvas); color:var(--ink); }
    .block-container { max-width:900px; padding-top:2.1rem; padding-bottom:2.5rem; }
    [data-testid="stHeader"] { background:var(--canvas); height:2.8rem; }
    .desktop { border:1px solid var(--line); background:var(--panel); box-shadow:3px 3px 0 #30343B; margin-bottom:1.35rem; }
    .titlebar { display:flex; justify-content:space-between; align-items:center; gap:12px; padding:10px 13px; background:#ECEEF2; color:#111318; border-bottom:1px solid #C8CBD1; font:600 .72rem 'IBM Plex Mono',monospace; text-transform:uppercase; letter-spacing:.02em; }
    .title-left { display:flex; gap:9px; align-items:center; min-width:0; }
    .title-left span:last-child { overflow-wrap:anywhere; }
    .controls { display:flex; gap:5px; flex-shrink:0; }
    .control { width:17px; height:17px; display:grid; place-items:center; border:1px solid #17191D; background:#fff; color:#111; font:700 11px 'IBM Plex Mono',monospace; }
    .control.close { background:var(--red); color:white; }
    .menu { display:flex; gap:17px; padding:7px 13px; border-bottom:1px solid var(--line); color:var(--muted); font:.68rem 'IBM Plex Mono',monospace; }
    .hero { padding:23px; }
    .eyebrow { color:var(--red); font:600 .68rem 'IBM Plex Mono',monospace; letter-spacing:.13em; text-transform:uppercase; }
    .hero h1 { color:var(--ink); font-size:clamp(1.7rem,4vw,2.4rem); line-height:1.1; letter-spacing:-.045em; margin:10px 0; }
    .hero p { color:var(--muted); font-size:.92rem; line-height:1.55; margin:0; max-width:640px; }
    .legend { display:flex; gap:8px; flex-wrap:wrap; margin-top:18px; }
    .pill { display:inline-flex; align-items:center; gap:7px; border:1px solid var(--line); padding:6px 9px; font:600 .65rem 'IBM Plex Mono',monospace; }
    .dot { width:7px; height:7px; border-radius:50%; display:inline-block; }
    .safe-dot { background:var(--green); } .spam-dot { background:var(--red); }
    .section { border:1px solid var(--line); background:var(--panel); padding:18px; margin:14px 0; }
    .section-title { font:600 .72rem 'IBM Plex Mono',monospace; text-transform:uppercase; letter-spacing:.07em; color:var(--muted); margin-bottom:13px; }
    .result { border:1px solid var(--line); border-left:4px solid var(--green); padding:17px; margin:14px 0; background:linear-gradient(90deg,var(--green-soft),var(--panel) 65%); }
    .result.scam { border-left-color:var(--red); background:linear-gradient(90deg,var(--red-soft),var(--panel) 65%); }
    .result.caution { border-left-color:var(--amber); background:linear-gradient(90deg,var(--amber-soft),var(--panel) 65%); }
    .verdict { font:700 1.2rem 'IBM Plex Mono',monospace; color:var(--green); }
    .verdict.scam { color:var(--red); } .verdict.caution { color:var(--amber); }
    .result-headline { font-size:1rem; font-weight:600; margin-top:8px; color:var(--ink); }
    .result-copy { color:#E4E6EA; line-height:1.6; font-size:.88rem; margin-top:10px; overflow-wrap:anywhere; white-space:pre-wrap; }
    .metric-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:14px 0; }
    .metric { background:var(--panel-raised); border:1px solid var(--line); padding:12px; min-width:0; }
    .metric-label { color:var(--muted); font:600 .63rem 'IBM Plex Mono',monospace; text-transform:uppercase; letter-spacing:.04em; }
    .metric-value { color:var(--ink); font:600 1.25rem 'IBM Plex Mono',monospace; margin-top:6px; overflow-wrap:anywhere; }
    .flag { border-left:2px solid var(--red); padding:8px 11px; background:#171316; margin:8px 0; }
    .advice { border-left:2px solid var(--green); padding:8px 11px; background:#111A16; margin:8px 0; }
    .muted { color:var(--muted); font-size:.76rem; line-height:1.5; }
    .status { display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px 16px; padding:10px 12px; margin-top:22px; background:var(--panel); border:1px solid var(--line); color:var(--muted); font:.65rem 'IBM Plex Mono',monospace; text-transform:uppercase; }
    div.stButton > button, div[data-testid="stDownloadButton"] button { border:1px solid #D8DCE3 !important; border-radius:2px !important; background:#ECEEF2 !important; color:#111318 !important; font:700 .75rem 'IBM Plex Mono',monospace !important; min-height:42px; box-shadow:2px 2px 0 #515660 !important; }
    div.stButton > button:hover, div[data-testid="stDownloadButton"] button:hover { background:#fff !important; color:#111318 !important; }
    div.stButton > button[kind="primary"] { background:var(--red) !important; color:#fff !important; border-color:#FF737D !important; box-shadow:2px 2px 0 #7D242C !important; }
    div[data-baseweb="textarea"] textarea, div[data-baseweb="select"] > div { border:1px solid #414650 !important; border-radius:2px !important; background:var(--panel-raised) !important; color:var(--ink) !important; font-family:'IBM Plex Mono',monospace !important; }
    label, [data-testid="stWidgetLabel"] { color:#DDE0E5 !important; }
    .stAlert { border-radius:2px !important; }
    @media(max-width:650px) {
        .hero,.section { padding:14px; }
        .block-container { padding-left:1rem; padding-right:1rem; }
        .metric-grid { grid-template-columns:1fr; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# LOAD MODELS
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_models():
    model_path = config.MODEL_DIR / "scamshield.joblib"
    baseline_path = config.MODEL_DIR / "baseline.joblib"
    try:
        model = joblib.load(model_path)
        baseline = joblib.load(baseline_path)
        retriever = Retriever(config.KB_PATH)
        return model, baseline, retriever
    except FileNotFoundError:
        return None


# ---------------------------------------------------------------------------
# EXAMPLES
# ---------------------------------------------------------------------------
EXAMPLES = {
    "KYC scam": "Dear SBI customer, your KYC has expired and your account will be blocked today. Update now: http://bit.ly/3xKyc9",
    "Electricity scam (Hinglish)": "Aapka bijli connection aaj raat kat jayega. Turant call karein 9876543210",
    "UPI refund scam": "Rs 4,999 refund received by mistake. Please approve the UPI collect request to return it immediately.",
    "Genuine OTP": "482913 is your OTP for Swiggy. Valid for 10 minutes. Do not share it with anyone.",
    "Friend text": "Bhai kal 5 baje milte hain canteen mein",
}

if "scamshield_text" not in st.session_state:
    st.session_state.scamshield_text = ""
if "scamshield_result" not in st.session_state:
    st.session_state.scamshield_result = None


# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="desktop">
      <div class="titlebar">
        <div class="title-left"><span>🛡</span><span>C:\\SYSTEM32\\SCAMSHIELD.EXE</span></div>
        <div class="controls"><span class="control">_</span><span class="control">□</span><span class="control close">×</span></div>
      </div>
      <div class="menu"><span><u>F</u>ile</span><span><u>A</u>nalysis</span><span><u>H</u>elp</span></div>
      <div class="hero">
        <div class="eyebrow">SCAMSHIELD / MESSAGE SAFETY</div>
        <h1>ScamShield</h1>
        <p>Check suspicious SMS messages, understand the warning signs, and get practical next steps. Designed for Indian-context scam patterns.</p>
        <div class="legend">
          <span class="pill"><span class="dot spam-dot"></span>SCAM / THREAT</span>
          <span class="pill"><span class="dot safe-dot"></span>LIKELY LEGITIMATE</span>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# SIMPLE DETECTOR WORKFLOW
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">01 / CHECK A MESSAGE</div>', unsafe_allow_html=True)

sample_col, attack_col = st.columns([1.4, 1], gap="medium")
with sample_col:
    selected_example = st.selectbox("Try an example", ["Type your own message"] + list(EXAMPLES))
with attack_col:
    attack_options = ["None"] + list(ATTACKS.keys())
    selected_attack_label = st.selectbox("Obfuscation test (optional)", attack_options)

if selected_example != "Type your own message" and st.button("USE EXAMPLE", use_container_width=True):
    st.session_state.scamshield_text = EXAMPLES[selected_example]
    st.rerun()

message = st.text_area(
    "SMS message",
    key="scamshield_text",
    height=145,
    placeholder="Paste the SMS here...",
    help="Use the optional obfuscation test to see how text manipulation may affect detection.",
)

def clear_all():
    """Clear the message and previous result before Streamlit redraws widgets."""
    st.session_state.scamshield_text = ""
    st.session_state.scamshield_result = None


analyze_col, clear_col = st.columns([1.5, 1], gap="small")
with analyze_col:
    analyze_clicked = st.button("ANALYSE MESSAGE", type="primary", use_container_width=True)
with clear_col:
    st.button("CLEAR", on_click=clear_all, use_container_width=True)


if analyze_clicked:
    if not message.strip():
        st.warning("Paste an SMS message before analysing it.")
    else:
        try:
            with st.spinner("Checking message..."):
                bundle = load_models()
                if bundle is None:
                    st.error("Trained models were not found. Run `python src/build_indian_data.py` and then `python src/train.py`.")
                    st.stop()

                model, baseline, retriever = bundle
                analysed_text = message
                if selected_attack_label != "None":
                    attack_fn = ATTACKS[selected_attack_label]
                    analysed_text = attack_fn(message, random.Random(3))

                result = explain(analysed_text, model, retriever)
                baseline_probability = None
                if hasattr(baseline, "predict_proba"):
                    baseline_probability = float(baseline.predict_proba([analysed_text])[0])

                if result["is_scam"]:
                    verdict_class, verdict_label = "scam", "SCAM DETECTED"
                elif len(result.get("red_flags", [])) >= 3:
                    verdict_class, verdict_label = "caution", "USE CAUTION"
                else:
                    verdict_class, verdict_label = "", "LIKELY LEGITIMATE"

                st.session_state.scamshield_result = {
                    "analysed_text": analysed_text,
                    "original_text": message,
                    "attack_name": selected_attack_label,
                    "result": result,
                    "baseline_probability": baseline_probability,
                    "verdict_class": verdict_class,
                    "verdict_label": verdict_label,
                }
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")


# ---------------------------------------------------------------------------
# RESULTS — ONLY SHOWN AFTER ANALYSIS
# ---------------------------------------------------------------------------
saved = st.session_state.scamshield_result
if saved:
    result = saved["result"]
    cls = saved["verdict_class"]
    label = saved["verdict_label"]
    scam_probability = float(result.get("scam_probability", 0.0))
    baseline_probability = saved["baseline_probability"]

    st.markdown("---")
    st.markdown('<div class="section-title">02 / ANALYSIS RESULT</div>', unsafe_allow_html=True)

    if saved["attack_name"] != "None":
        st.info(f"Obfuscation test applied: {saved['attack_name']}. The result below is for the modified message.")
        with st.expander("View modified message"):
            st.write(saved["analysed_text"])

    st.markdown(
        f"""
        <div class="result {cls}">
          <div class="verdict {cls}">{html.escape(label)}</div>
          <div class="result-headline">{html.escape(str(result.get('headline', 'Analysis complete')))}</div>
          <div class="result-copy">{html.escape(str(result.get('why', 'No additional explanation was returned.')))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_markup = f"""
    <div class="metric-grid">
      <div class="metric">
        <div class="metric-label">ScamShield scam score</div>
        <div class="metric-value">{scam_probability * 100:.0f}%</div>
      </div>
      <div class="metric">
        <div class="metric-label">Baseline model score</div>
        <div class="metric-value">{f'{baseline_probability * 100:.0f}%' if baseline_probability is not None else 'N/A'}</div>
      </div>
    </div>
    """
    st.markdown(metric_markup, unsafe_allow_html=True)

    red_flags = result.get("red_flags", [])
    if red_flags:
        st.markdown("**Warning signs**")
        for flag in red_flags:
            st.markdown(
                f'<div class="flag"><strong>{html.escape(str(flag.get("flag", "Warning sign")))}</strong><br><span class="muted">{html.escape(str(flag.get("why", "")))}</span></div>',
                unsafe_allow_html=True,
            )

    advice = result.get("advice", [])
    if advice:
        st.markdown("**Recommended next steps**")
        for item in advice:
            st.markdown(
                f'<div class="advice">{html.escape(str(item))}</div>',
                unsafe_allow_html=True,
            )

    with st.expander("Knowledge-base references"):
        sources = result.get("sources", [])
        if sources:
            for title, similarity in sources:
                st.write(f"{title} · similarity {similarity}")
        else:
            st.caption("No knowledge-base entries were returned for this message.")

    st.caption("This is an advisory model output, not a guarantee. Verify links, payment requests, and helpline details independently.")


# ---------------------------------------------------------------------------
# OPTIONAL MODEL RESULTS
# ---------------------------------------------------------------------------
with st.expander("Model performance (optional)"):
    metrics_path = config.RESULTS_DIR / "metrics.csv"
    robustness_path = config.RESULTS_DIR / "robustness.csv"
    if metrics_path.exists() and robustness_path.exists():
        try:
            metrics = pd.read_csv(metrics_path)
            robustness = pd.read_csv(robustness_path)
            st.markdown("**F1 on clean test sets**")
            if {"model", "test_set", "f1"}.issubset(metrics.columns):
                st.dataframe(
                    metrics.pivot(index="model", columns="test_set", values="f1").round(3),
                    use_container_width=True,
                )
            else:
                st.dataframe(metrics, use_container_width=True, hide_index=True)

            st.markdown("**Scam recall under obfuscation tests**")
            if {"model", "attack", "recall"}.issubset(robustness.columns):
                st.dataframe(
                    robustness.pivot(index="model", columns="attack", values="recall").round(2),
                    use_container_width=True,
                )
            else:
                st.dataframe(robustness, use_container_width=True, hide_index=True)

            for image_name in ("f1_comparison.png", "robustness_heatmap.png"):
                image_path = config.RESULTS_DIR / image_name
                if image_path.exists():
                    st.image(str(image_path), use_container_width=True)
        except Exception as exc:
            st.warning(f"Could not display model results: {exc}")
    else:
        st.caption("Evaluation files are not available yet. Run `python src/train.py` to generate them.")


# ---------------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="status">
      <span>SCAMSHIELD.EXE</span>
      <span>LOCAL ANALYSIS</span>
      <span>INDIAN SMS SCAM DETECTION</span>
    </div>
    <p class="muted" style="margin-top:12px">Safety note: Never share OTPs, UPI PINs, passwords, or remote-access codes. Do not open suspicious links just to test them.</p>
    """,
    unsafe_allow_html=True,
)
