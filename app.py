import streamlit as st
import json
import re
import os
import time
import pandas as pd
from groq import Groq
from difflib import SequenceMatcher

# ------------------------------------------------------------
# Page config - full width, no padding, custom layout
# ------------------------------------------------------------
st.set_page_config(
    page_title="PROMPT NEXUS // COMMAND CENTER",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------
# 1. ADVANCED FUTURISTIC STYLES (No Sidebar, Immersive UI)
# ------------------------------------------------------------
def inject_futuristic_ui():
    st.markdown("""
    <style>
    /* ====== FONTS ====== */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600&family=Space+Mono&display=swap');

    /* ====== GLOBAL RESET ====== */
    .stApp {
        background: #050914;
        color: #d0e0ff;
        font-family: 'Inter', sans-serif;
        overflow-x: hidden;
    }

    /* Hide default sidebar completely */
    [data-testid="stSidebar"] {
        display: none;
    }

    /* Remove default padding */
    .main .block-container {
        padding: 1rem 2rem !important;
        max-width: 100%;
    }

    /* ====== SCANNING LINE OVERLAY ====== */
    .stApp::after {
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 2px;
        background: rgba(0, 255, 255, 0.4);
        box-shadow: 0 0 20px rgba(0,255,255,0.6);
        animation: scan 8s linear infinite;
        z-index: 9999;
        pointer-events: none;
    }
    @keyframes scan {
        0% { top: -2px; }
        100% { top: 100%; }
    }

    /* ====== TOP HUD BAR ====== */
    .top-hud {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background: rgba(10, 20, 40, 0.7);
        backdrop-filter: blur(25px);
        border-bottom: 1px solid rgba(0, 255, 255, 0.2);
        margin-bottom: 2rem;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }
    .hud-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2em;
        color: #00ccff;
        text-shadow: 0 0 15px #00ccff;
        letter-spacing: 5px;
    }
    .status-lights {
        display: flex;
        gap: 20px;
        font-family: 'Space Mono', monospace;
        color: #aaa;
    }
    .status-light {
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00ff88;
        box-shadow: 0 0 10px #00ff88;
    }

    /* ====== FILTER BAR ====== */
    .filter-bar {
        display: flex;
        gap: 2rem;
        background: rgba(15, 25, 45, 0.8);
        backdrop-filter: blur(10px);
        padding: 1rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 1px solid rgba(0, 255, 255, 0.3);
    }

    /* ====== PROMPT CARD GRID ====== */
    .prompt-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-bottom: 2rem;
    }
    .prompt-card {
        background: rgba(18, 28, 50, 0.9);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(0, 255, 255, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(0,0,0,0.5);
        cursor: pointer;
    }
    .prompt-card:hover {
        border-color: #00ccff;
        box-shadow: 0 0 30px rgba(0, 204, 255, 0.4);
        transform: translateY(-5px);
    }
    .card-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.2em;
        color: #00ccff;
        margin-bottom: 0.5rem;
    }
    .card-meta {
        font-size: 0.8em;
        color: #8899cc;
        display: flex;
        gap: 10px;
    }

    /* ====== OUTPUT BAY (slide-up) ====== */
    .output-bay {
        position: fixed;
        bottom: 0; left: 0;
        width: 100%;
        background: rgba(5, 9, 20, 0.95);
        backdrop-filter: blur(30px);
        border-top: 2px solid #00ccff;
        box-shadow: 0 -10px 30px rgba(0, 0, 0, 0.8);
        z-index: 999;
        padding: 2rem;
        transition: transform 0.4s ease-in-out;
        transform: translateY(0%);
    }
    .bay-hidden {
        transform: translateY(100%);
    }

    /* ====== BUTTONS ====== */
    .stButton > button {
        background: rgba(0, 204, 255, 0.15);
        border: 1px solid #00ccff;
        color: #00ccff;
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        transition: all 0.3s;
        box-shadow: 0 0 15px rgba(0,204,255,0.2);
    }
    .stButton > button:hover {
        background: rgba(0, 204, 255, 0.3);
        box-shadow: 0 0 30px rgba(0,204,255,0.6);
        color: white;
        transform: scale(1.02);
    }

    /* ====== INPUTS ====== */
    .stTextInput > div > div > input, .stTextArea textarea {
        background: rgba(10, 20, 40, 0.8) !important;
        border: 1px solid #00ccff !important;
        color: #d0e0ff !important;
        border-radius: 8px;
    }

    /* ====== SCROLLBAR ====== */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #050914; }
    ::-webkit-scrollbar-thumb { background: #00ccff; border-radius: 3px; }
    </style>
    """, unsafe_allow_html=True)

inject_futuristic_ui()

# ------------------------------------------------------------
# Load prompt library
# ------------------------------------------------------------
@st.cache_data
def load_prompts():
    with open("prompts_library.json", "r", encoding="utf-8") as f:
        return json.load(f)

prompts_db = load_prompts()

# ------------------------------------------------------------
# Groq helper
# ------------------------------------------------------------
def groq_chat(prompt_text, model="llama-3.1-8b-instant", temperature=0.3, max_tokens=400):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    start = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt_text}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    latency = time.time() - start
    output = response.choices[0].message.content
    usage = response.usage.total_tokens if response.usage else None
    return output, latency, usage

# ------------------------------------------------------------
# Heuristic analysis (same as before)
# ------------------------------------------------------------
def analyze_prompt_heuristic(prompt_text):
    score = 0
    feedback = []
    words = prompt_text.split()
    if len(words) < 5:
        feedback.append("Very short prompt; may lack context.")
        score += 1
    elif len(words) > 100:
        feedback.append("Extremely long prompt; may be overly complex.")
        score += 3
    else:
        score += 5

    if re.search(r"you are a[n]?\s+", prompt_text, re.IGNORECASE):
        feedback.append("✅ Role assignment found.")
        score += 2
    else:
        feedback.append("❌ No role assignment – consider adding persona.")

    if "step" in prompt_text.lower() or "1." in prompt_text or "first" in prompt_text.lower():
        feedback.append("✅ Step‑by‑step structure detected.")
        score += 2
    else:
        feedback.append("❌ No step‑by‑step structure.")

    if re.search(r"example|e\.g\.|for instance", prompt_text, re.IGNORECASE):
        feedback.append("✅ Examples provided.")
        score += 1

    if "if you don't know" in prompt_text.lower() or "do not make up" in prompt_text.lower():
        feedback.append("✅ Anti‑hallucination clause found.")
        score += 1
    else:
        feedback.append("❌ No anti‑hallucination clause.")

    final_score = min(10, score)
    return final_score, feedback

# ------------------------------------------------------------
# AI evaluator (optional)
# ------------------------------------------------------------
def ai_evaluate_prompt(prompt_text):
    meta_prompt = f"""You are an expert prompt engineer. Analyze the following prompt for clarity, specificity, and potential issues.
Provide a rating out of 10 and a brief justification.

Prompt:
\"\"\"
{prompt_text}
\"\"\"

Analysis:"""
    output, _, _ = groq_chat(meta_prompt, temperature=0.1, max_tokens=200)
    return output

# ------------------------------------------------------------
# TOP HUD (HTML)
# ------------------------------------------------------------
st.markdown("""
<div class="top-hud">
    <div class="hud-title">⚡ PROMPT NEXUS</div>
    <div class="status-lights">
        <div class="status-light"><span class="status-dot"></span> Neural Engine: ONLINE</div>
        <div class="status-light"><span class="status-dot"></span> Groq Interface: CONNECTED</div>
        <div class="status-light"><span class="status-dot"></span> Encryption: ACTIVE</div>
    </div>
    <div style="font-family: Orbitron; color: #00ccff; font-size: 0.9em;">⌘ COMMAND CENTER v3.0</div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# FILTER BAR (using columns to mimic custom bar)
# ------------------------------------------------------------
col1, col2, col3 = st.columns([2,2,1])
with col1:
    categories = ["All"] + sorted(list(set(p["category"] for p in prompts_db)))
    selected_category = st.selectbox("CATEGORY", categories, label_visibility="collapsed")
with col2:
    genres = ["All"] + sorted(list(set(p["genre"] for p in prompts_db)))
    selected_genre = st.selectbox("GENRE", genres, label_visibility="collapsed")
with col3:
    if st.button("➕ ADD PROMPT"):
        st.session_state.show_add_form = True

# Filter prompts
filtered_prompts = prompts_db
if selected_category != "All":
    filtered_prompts = [p for p in filtered_prompts if p["category"] == selected_category]
if selected_genre != "All":
    filtered_prompts = [p for p in filtered_prompts if p["genre"] == selected_genre]

# ------------------------------------------------------------
# PROMPT CARD GRID (custom HTML + Streamlit buttons inside columns)
# ------------------------------------------------------------
st.markdown(f"## 📡 PROMPT LIBRARY ({len(filtered_prompts)} signals detected)")

# Show cards in rows of 3
num_cols = 3
for i in range(0, len(filtered_prompts), num_cols):
    cols = st.columns(num_cols)
    for j in range(num_cols):
        idx = i + j
        if idx >= len(filtered_prompts):
            break
        prompt = filtered_prompts[idx]
        with cols[j]:
            # Card container with custom styling
            st.markdown(f"""
            <div class="prompt-card" id="card-{prompt['id']}">
                <div class="card-title">{prompt['title']}</div>
                <div class="card-meta">
                    <span>{prompt['category']}</span> | <span>{prompt['genre']}</span>
                </div>
                <p style="font-size:0.85em; color:#aabbdd; margin-top:10px;">{prompt['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Button to run the prompt
            if st.button(f"▶️ RUN", key=f"run_{prompt['id']}"):
                st.session_state.selected_prompt = prompt
                st.session_state.run_trigger = True

# ------------------------------------------------------------
# OUTPUT BAY (slides up when a prompt is run)
# ------------------------------------------------------------
if "selected_prompt" in st.session_state and st.session_state.get("run_trigger", False):
    prompt = st.session_state.selected_prompt
    st.markdown('<div class="output-bay">', unsafe_allow_html=True)
    
    st.markdown(f"### ⚡ EXECUTING: {prompt['title']}")
    
    # Variable injection
    var_dict = {}
    if prompt.get("variables"):
        cols = st.columns(len(prompt["variables"]))
        for i, var in enumerate(prompt["variables"]):
            with cols[i]:
                var_dict[var] = st.text_input(f"⏺️ {var}", key=f"var_{prompt['id']}_{var}")
    else:
        var_dict = {}
    
    final_prompt = prompt["prompt_template"]
    for var, val in var_dict.items():
        if val:
            final_prompt = final_prompt.replace("{" + var + "}", val)
    
    remaining_vars = re.findall(r"\{(\w+)\}", final_prompt)
    if remaining_vars:
        st.warning(f"Fill remaining placeholders: {', '.join(remaining_vars)}")
    else:
        if not os.environ.get("GROQ_API_KEY"):
            st.error("GROQ_API_KEY not set.")
        else:
            if st.button("🚀 EXECUTE PROMPT", key="exec_btn"):
                with st.spinner("⚡ Neural pathway engaged..."):
                    output, latency, tokens = groq_chat(final_prompt)
                    st.markdown("### 🌀 OUTPUT")
                    st.code(output, language="text")
                    st.caption(f"⏱️ {latency:.2f}s | 🧠 {tokens} tokens")
                    
                    # Heuristic analysis
                    score, fb = analyze_prompt_heuristic(final_prompt)
                    st.markdown("### 🛡️ PROMPT QUALITY SCORE")
                    st.metric("Score", f"{score}/10")
                    for f in fb:
                        st.write(f)
                    
                    # AI deep eval
                    if st.button("🔬 DEEP AI EVALUATION", key="deep_eval"):
                        with st.spinner("Analyzing prompt architecture..."):
                            ai_fb = ai_evaluate_prompt(final_prompt)
                            st.markdown("### 🤖 AI FEEDBACK")
                            st.write(ai_fb)
    
    if st.button("❌ CLOSE OUTPUT BAY"):
        st.session_state.run_trigger = False
        st.experimental_rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# ADD PROMPT FORM (slide-in modal style)
# ------------------------------------------------------------
if st.session_state.get("show_add_form", False):
    with st.container():
        st.markdown("---")
        st.header("➕ NEW PROMPT CONFIGURATION")
        with st.form("add_form"):
            title = st.text_input("Title")
            category = st.selectbox("Category", categories[1:])
            genre = st.selectbox("Genre", genres[1:])
            description = st.text_area("Description")
            prompt_template = st.text_area("Prompt template (use {var} placeholders)")
            submitted = st.form_submit_button("💾 SAVE TO LIBRARY")
            if submitted:
                new_id = max(p["id"] for p in prompts_db) + 1
                new_prompt = {
                    "id": new_id,
                    "title": title,
                    "category": category,
                    "genre": genre,
                    "prompt_template": prompt_template,
                    "description": description,
                    "variables": re.findall(r"\{(\w+)\}", prompt_template)
                }
                prompts_db.append(new_prompt)
                st.success(f"Prompt '{title}' added!")
                st.session_state.show_add_form = False
                st.experimental_rerun()
        if st.button("Cancel"):
            st.session_state.show_add_form = False
            st.experimental_rerun()

# Export option
st.markdown("---")
if st.button("📦 EXPORT LIBRARY"):
    st.download_button(
        label="Download JSON",
        data=json.dumps(prompts_db, indent=2),
        file_name="prompts_library.json",
        mime="application/json"
    )