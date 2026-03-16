import streamlit as st
import streamlit.components.v1 as components
import json
import re
import requests

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AMR.viz — Powered by Groq",
    page_icon="🔬",
    layout="wide",
)

# ── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Fraunces:ital,wght@0,300;0,600;1,300&display=swap');

html, body, [class*="css"] { font-family: 'DM Mono', monospace; }

.main-header {
    background: #0f0f0d; color: #f7f5f0;
    padding: 1.4rem 2rem; border-radius: 10px;
    border-bottom: 3px solid #f55036;
    margin-bottom: 1.5rem;
    display: flex; align-items: flex-end; gap: 1rem;
}
.logo { font-family: 'Fraunces', serif; font-size: 2rem; font-weight: 600; line-height:1; }
.logo span { color: #f55036; }
.tagline { font-size: 0.65rem; color: #888880; letter-spacing: 0.1em; text-transform: uppercase; padding-bottom: 3px; }
.powered { font-size: 0.6rem; color: #f55036; letter-spacing: 0.08em; text-transform: uppercase; padding-bottom: 3px; margin-left: auto; }

.spell-banner {
    background: #fff8e6; border: 1.5px solid #f0c040;
    border-radius: 8px; padding: 0.8rem 1rem;
    font-size: 0.8rem; color: #7a5c00; margin-bottom: 1rem; line-height: 1.6;
}
.nonsense-banner {
    background: #fff0f0; border: 1.5px solid #e88;
    border-radius: 8px; padding: 0.8rem 1rem;
    font-size: 0.8rem; color: #a33; margin-bottom: 1rem;
}
.lang-banner {
    background: #edf7f2; border: 1.5px solid #1a6b4a;
    border-radius: 8px; padding: 0.9rem 1.1rem;
    font-size: 0.82rem; color: #1a4a35; margin-bottom: 1rem; line-height: 1.8;
}
.word-map-table { width: 100%; border-collapse: collapse; font-size: 0.78rem; margin-top: 4px; }
.word-map-table th {
    text-align: left; font-size: 0.65rem; text-transform: uppercase;
    letter-spacing: 0.08em; color: #7a7a72;
    padding: 0 10px 8px 0; border-bottom: 1.5px solid #e4e0d8; font-weight: 500;
}
.word-map-table td {
    padding: 7px 10px 7px 0; border-bottom: 1px solid #eeebe4;
    vertical-align: top; color: #3a3a35; line-height: 1.5;
}
.word-map-table tr:last-child td { border-bottom: none; }
.src-word { font-weight: 500; color: #0f0f0d; font-size: 0.85rem; }
.translit  { font-size: 0.7rem; color: #7a7a72; font-style: italic; display:block; margin-top:1px; }
.expl-sentence {
    font-family: 'Fraunces', serif;
    font-size: 1.2rem; font-style: italic; font-weight: 300;
    color: #0f0f0d; margin-bottom: 0.5rem; line-height: 1.5;
}
.expl-text { font-size: 0.82rem; color: #3a3a35; line-height: 1.8; }

.amr-block {
    background: #f7f5f0; border: 1.5px solid #e4e0d8;
    border-radius: 8px; padding: 1rem 1.2rem;
    font-family: 'DM Mono', monospace; font-size: 0.78rem;
    line-height: 2; overflow-x: auto; white-space: pre;
}
.amr-var     { color: #1a4a6b; font-weight: 500; }
.amr-concept { color: #1a6b4a; }
.amr-role    { color: #c4501a; }
.amr-lit     { color: #b8860b; }

.node-table { width: 100%; border-collapse: collapse; font-size: 0.78rem; }
.node-table th {
    text-align: left; font-size: 0.65rem; text-transform: uppercase;
    letter-spacing: 0.08em; color: #7a7a72;
    padding: 0 10px 8px 0; border-bottom: 1.5px solid #e4e0d8; font-weight: 500;
}
.node-table td {
    padding: 8px 10px 8px 0; border-bottom: 1px solid #eeebe4;
    vertical-align: top; color: #3a3a35; line-height: 1.5;
}
.node-table tr:last-child td { border-bottom: none; }
.var-badge  { background:#e6f1fb; color:#0c447c; border-radius:4px; padding:1px 7px; font-family:'DM Mono',monospace; font-size:0.72rem; font-weight:500; }
.con-badge  { background:#eaf3de; color:#27500a; border-radius:4px; padding:1px 7px; font-family:'DM Mono',monospace; font-size:0.72rem; }
.role-badge { background:#faeeda; color:#633806; border-radius:4px; padding:1px 7px; font-family:'DM Mono',monospace; font-size:0.72rem; }
.section-label {
    font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.1em;
    color: #7a7a72; margin-bottom: 0.5rem;
}

/* ── Deep explanation panel ── */
.deep-wrap { display: flex; flex-direction: column; gap: 14px; }
.deep-card {
    border: 1px solid #e4e0d8; border-radius: 8px; overflow: hidden;
}
.deep-card-head {
    background: #f0ede6; padding: 8px 14px;
    font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.09em;
    color: #5a5a52; font-weight: 500;
    display: flex; align-items: center; gap: 7px;
}
.deep-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.deep-card-body { padding: 13px 16px; background: #faf9f6; }
.deep-summary {
    font-family: 'Fraunces', serif; font-size: 1rem; font-weight: 300;
    font-style: italic; color: #0f0f0d; line-height: 1.6;
}
.deep-text { font-size: 0.8rem; color: #3a3a35; line-height: 1.75; }
.deep-label { font-size: 0.72rem; font-weight: 500; color: #0f0f0d; margin-bottom: 2px; }
.role-row {
    display: flex; gap: 10px; align-items: flex-start;
    padding: 9px 0; border-bottom: 1px solid #eeebe4;
}
.role-row:last-child { border-bottom: none; padding-bottom: 0; }
.role-pill {
    font-family: 'DM Mono', monospace; font-size: 0.7rem;
    background: #faeeda; color: #633806;
    border-radius: 4px; padding: 2px 8px; white-space: nowrap; flex-shrink: 0;
}
.role-concept {
    font-family: 'DM Mono', monospace; font-size: 0.7rem;
    background: #eaf3de; color: #27500a;
    border-radius: 4px; padding: 2px 8px; white-space: nowrap; flex-shrink: 0;
}
.role-desc { font-size: 0.78rem; color: #3a3a35; line-height: 1.6; }
.feature-row {
    padding: 8px 0; border-bottom: 1px solid #eeebe4;
    display: flex; gap: 10px; align-items: flex-start;
}
.feature-row:last-child { border-bottom: none; padding-bottom: 0; }
.feature-tag {
    font-size: 0.68rem; font-weight: 500; background: #e6f1fb; color: #0c447c;
    border-radius: 4px; padding: 2px 8px; white-space: nowrap; flex-shrink: 0;
}
.ignore-box {
    background: #f7f5f0; border-left: 3px solid #c8c6be;
    border-radius: 0 6px 6px 0; padding: 10px 14px;
    font-size: 0.78rem; color: #5a5a52; line-height: 1.7;
}
.propbank-box {
    background: #edf7f2; border-left: 3px solid #1a6b4a;
    border-radius: 0 6px 6px 0; padding: 10px 14px;
    font-size: 0.78rem; color: #1a4a35; line-height: 1.7;
}
div[data-testid="stTextInput"] input {
    font-family: 'DM Mono', monospace !important; font-size: 0.9rem !important;
    border-radius: 6px !important;
}
div[data-testid="stButton"] button {
    background: #f55036 !important; color: #ffffff !important;
    border: none !important; border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important; font-weight: 500 !important;
}
div[data-testid="stButton"] button:hover { background: #c73d28 !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <div>
    <div class="logo">AMR<span>.</span>viz</div>
  </div>
  <div class="tagline">Abstract Meaning Representation · Live Parser</div>
  <div class="powered">Powered by Groq · Free · No quota issues</div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Configuration")
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        api_key = st.sidebar.text_input(
            "Groq API Key",
            type="password",
            placeholder="gsk_...",
            help="Get your free key at console.groq.com",
        )
        st.caption("Free · No credit card · Very fast")

    st.markdown("---")

    # ── Smart suggestions (shown after a parse) ─────────────────────────────
    sugg = st.session_state.get("suggestions", {})
    last_sentence = st.session_state.get("amr_sentence", "")

    if sugg and last_sentence:
        st.markdown("### Smart suggestions")
        st.caption(f'Based on: *"{last_sentence[:40]}{"…" if len(last_sentence)>40 else ""}"*')

        # Try these next
        try_next = sugg.get("try_next", [])
        if try_next:
            st.markdown("**Try these next**")
            for s in try_next:
                if st.button(s, key=f"sugg_try_{s[:30]}"):
                    st.session_state["sentence"] = s
                    st.session_state["sentence_input"] = s
                    st.session_state["_auto_parse"] = True
                    st.rerun()

        # Contrast sentences
        contrast = sugg.get("contrast", [])
        if contrast:
            st.markdown("**See the contrast**")
            for s in contrast:
                if st.button(s, key=f"sugg_con_{s[:30]}"):
                    st.session_state["sentence"] = s
                    st.session_state["sentence_input"] = s
                    st.session_state["_auto_parse"] = True
                    st.rerun()

        # Learn tips
        learn = sugg.get("learn", [])
        if learn:
            st.markdown("**AMR tips from this parse**")
            for item in learn:
                tip  = item.get("tip", "")
                ex   = item.get("example", "")
                with st.expander(tip):
                    st.caption(ex)
                    if st.button(f"Try: {ex[:35]}…" if len(ex)>35 else f"Try: {ex}",
                                 key=f"sugg_learn_{ex[:25]}"):
                        st.session_state["sentence"] = ex
                        st.session_state["sentence_input"] = ex
                        st.session_state["_auto_parse"] = True
                        st.rerun()

        st.markdown("---")

    # ── Static examples (always shown) ─────────────────────────────────────
    st.markdown("**Example sentences**")

    lang_examples = {
        "English":  ["The boy wants to go.", "She did not believe him.", "Obama went to Paris.", "The company fired fifty workers."],
        "Hindi":    ["लड़का जाना चाहता है।", "उसने उस पर विश्वास नहीं किया।", "वैज्ञानिक ने एक नई दवा खोजी।"],
        "Kannada":  ["ಹುಡುಗನು ಹೋಗಲು ಬಯಸುತ್ತಾನೆ.", "ಅವಳು ಅವನನ್ನು ನಂಬಲಿಲ್ಲ.", "ವಿಜ್ಞಾನಿ ಹೊಸ ಔಷಧಿಯನ್ನು ಕಂಡುಹಿಡಿದರು."],
        "Telugu":   ["అబ్బాయి వెళ్ళాలని అనుకుంటున్నాడు.", "ఆమె అతన్ని నమ్మలేదు.", "శాస్త్రవేత్త కొత్త మందు కనుగొన్నాడు."],
        "Tamil":    ["சிறுவன் செல்ல விரும்புகிறான்.", "அவள் அவனை நம்பவில்லை.", "விஞ்ஞானி புதிய மருந்தை கண்டுபிடித்தார்."],
    }

    sel_lang = st.selectbox("Language", list(lang_examples.keys()), key="ex_lang_sel")
    for ex in lang_examples[sel_lang]:
        if st.button(ex, key=f"ex_{ex}"):
            st.session_state["sentence"] = ex
            st.session_state["sentence_input"] = ex
            st.session_state["_auto_parse"] = True
            st.rerun()

    st.markdown("---")
    st.markdown("""
**AMR Quick Reference**
- `root` = main event node
- `:ARG0` = agent (who does it)
- `:ARG1` = patient (what/whom)
- `:ARG2` = destination / beneficiary
- `:polarity -` = negation
- `:name` = named entity
""")


# ── Prompt ──────────────────────────────────────────────────────────────────
def build_prompt(sentence: str) -> str:
    return f"""You are a multilingual AMR (Abstract Meaning Representation) expert.
You can handle input in any language: English, Hindi, Kannada, Telugu, Tamil, or others.

INPUT SENTENCE: "{sentence}"

STEP 1 — Detect the language of the input.
STEP 2 — If not English, translate it to English accurately.
STEP 3 — Check for spelling mistakes in the (possibly translated) sentence. Correct any typos.
STEP 4 — Produce a complete AMR for the corrected English sentence.
STEP 5 — Write a rich explanation as described below.

Return ONLY a raw JSON object. No markdown fences. No text before or after the JSON.

{{
  "original": "exactly as typed by user",
  "detected_language": "English or Hindi or Kannada or Telugu or Tamil or other language name",
  "is_english": true or false,
  "translation": "English translation if not English, else same as original",
  "transliteration": "romanized version of non-English input for pronunciation help, empty string if English",
  "word_map": [
    {{"source_word": "ಹುಡುಗನು", "translation": "boy", "amr_role": ":ARG0", "note": "subject/agent"}}
  ],
  "corrected": "spell-corrected English version",
  "has_spelling_errors": false,
  "spelling_changes": [],
  "is_nonsense": false,
  "amr_notation": "AMR string with actual newlines and spaces for indentation",
  "explanation": "1-2 sentences about root concept and notable features. No internal double quotes.",
  "deep_explanation": {{
    "summary": "One plain-English sentence of what the full sentence means semantically.",
    "root_concept": {{
      "concept": "want-01",
      "why_root": "Plain English: why this is the main event of the sentence."
    }},
    "roles_explained": [
      {{
        "role": ":ARG0",
        "variable": "b",
        "concept": "boy",
        "plain_english": "The boy is the one who WANTS — he is the agent performing the wanting."
      }}
    ],
    "special_features": [],
    "what_amr_ignores": "AMR ignores tense, articles, and word order. It only captures core meaning.",
    "propbank_note": "want-01 comes from PropBank. The -01 means sense 1 of want."
  }},
  "nodes": [
    {{"variable":"w","concept":"want-01","role":"root","meaning":"wanting event"}},
    {{"variable":"b","concept":"boy","role":":ARG0","meaning":"who wants"}}
  ],
  "edges": [
    {{"from":"w","to":"b","label":":ARG0","is_reentrant":false}}
  ]
}}

STRICT RULES:
- AMR is ALWAYS in English regardless of input language — translate first then parse
- PropBank frames only (want-01, go-02, believe-01, discover-01, etc.)
- Variables: single lowercase letters only
- meaning: 5 words max
- All string values: no double-quotes inside
- special_features: only features that actually appear. Empty list [] if none.
- is_reentrant: true only for coreference
- Root node role must be exactly "root"
- word_map: map each content word from original to its English translation and AMR role. Skip articles and particles.
- Output complete valid JSON — do not truncate
"""


# ── Suggestions prompt ─────────────────────────────────────────────────────
def build_suggestions_prompt(sentence: str, nodes: list) -> str:
    concepts = ", ".join(n.get("concept", "") for n in nodes[:5])
    return f"""Given this sentence and its AMR concepts, generate smart follow-up suggestions.

Sentence: "{sentence}"
AMR concepts used: {concepts}

Return ONLY raw JSON — no markdown, no text outside JSON:
{{
  "try_next": [
    "A slightly more complex version of the same sentence",
    "Same sentence but negated",
    "Same sentence with a named entity added"
  ],
  "contrast": [
    "A sentence that uses the same root concept differently",
    "A sentence that shows coreference"
  ],
  "learn": [
    {{
      "tip": "Short AMR tip title",
      "example": "Example sentence showing that tip"
    }},
    {{
      "tip": "Another AMR tip title",
      "example": "Example sentence showing that tip"
    }}
  ]
}}

Rules:
- try_next: 3 sentences, each a natural variation of the input
- contrast: 2 sentences showing different AMR patterns
- learn: 2 tips directly relevant to the concepts in this AMR
- All strings short — under 60 characters
- No double quotes inside string values
- Return complete valid JSON only
"""

def fetch_suggestions(api_key: str, sentence: str, nodes: list) -> dict:
    try:
        raw = call_groq(api_key, build_suggestions_prompt(sentence, nodes))
        return safe_parse(raw)
    except Exception:
        return {}


# ── Groq API call ───────────────────────────────────────────────────────────
def call_groq(api_key: str, prompt: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "You are an AMR expert. Always respond with raw JSON only — no markdown, no explanation, no text outside the JSON object.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 2000,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if resp.status_code == 401:
        raise Exception("Invalid API key. Please check your Groq key (starts with gsk_).")
    if resp.status_code == 429:
        raise Exception("Rate limit hit — wait 10 seconds and try again.")
    if not resp.ok:
        raise Exception(f"Groq error {resp.status_code}: {resp.text[:200]}")
    return resp.json()["choices"][0]["message"]["content"]


# ── JSON repair ─────────────────────────────────────────────────────────────
def clean_json_string(text: str) -> str:
    """
    Robustly clean LLM JSON output.
    Handles:
      1. Markdown fences (```json ... ```)
      2. Raw control characters inside strings (\n \r \t etc.)
      3. Unescaped double-quotes inside string values  → the ',' delimiter error
      4. En-dashes / smart quotes / unicode punctuation that break strict JSON
    """
    # 1 — strip markdown fences and surrounding whitespace
    text = re.sub(r'^```(?:json)?\s*', '', text.strip(), flags=re.I)
    text = re.sub(r'\s*```$', '', text.strip())

    # 2 — extract the outermost { ... }
    f, l = text.find("{"), text.rfind("}")
    if f != -1 and l > f:
        text = text[f:l+1]

    # 3 — replace smart/curly quotes with plain ASCII quotes
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    # replace en-dash / em-dash inside strings with a hyphen
    text = text.replace('\u2013', '-').replace('\u2014', '-')

    # 4 — walk char-by-char to fix control chars AND unescaped inner quotes
    result      = []
    in_string   = False
    escape_next = False
    i = 0
    while i < len(text):
        ch = text[i]

        if escape_next:
            # whatever follows a backslash — keep as-is
            result.append(ch)
            escape_next = False
            i += 1
            continue

        if ch == '\\':
            result.append(ch)
            escape_next = True
            i += 1
            continue

        if ch == '"':
            if not in_string:
                # opening quote
                in_string = True
                result.append(ch)
            else:
                # Could be closing quote OR an unescaped inner quote.
                # Peek ahead: if next non-whitespace char is one of  : , } ]
                # then this IS the closing quote.
                j = i + 1
                while j < len(text) and text[j] in ' \t\r\n':
                    j += 1
                next_ch = text[j] if j < len(text) else ''
                if next_ch in (',', '}', ']', ':'):
                    # legitimate closing quote
                    in_string = False
                    result.append(ch)
                else:
                    # unescaped inner quote — escape it
                    result.append('\\"')
            i += 1
            continue

        if in_string:
            # fix raw control characters
            if ch == '\n':
                result.append('\\n')
            elif ch == '\r':
                result.append('\\r')
            elif ch == '\t':
                result.append('\\t')
            elif ord(ch) < 32:
                result.append(' ')
            else:
                result.append(ch)
        else:
            result.append(ch)
        i += 1

    return ''.join(result)


def safe_parse(text: str) -> dict:
    cleaned = clean_json_string(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Last resort: close any unclosed structures
        r = cleaned.rstrip().rstrip(",")
        if r.count('"') % 2 != 0:
            r += '"'
        r += "]" * max(0, r.count("[") - r.count("]"))
        r += "}" * max(0, r.count("{") - r.count("}"))
        try:
            return json.loads(r)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Could not repair JSON. Detail: {e.msg}", e.doc, e.pos
            )


# ── Animated graph builder ──────────────────────────────────────────────────
def build_animated_graph(nodes: list, edges: list) -> str:
    """
    Returns an HTML string containing an SVG graph that builds itself
    step-by-step with slow animation so learners can follow along.
    Steps: root node → child nodes level by level → edges one by one with labels.
    """
    if not nodes:
        return ""

    NW, NH, HGAP, VGAP = 118, 34, 24, 70
    root = next((n for n in nodes if n.get("role") == "root"), nodes[0])

    # Build level map via BFS
    child_map = {n["variable"]: [] for n in nodes}
    for e in edges:
        if not e.get("is_reentrant") and e.get("from") in child_map:
            target = next((n for n in nodes if n["variable"] == e.get("to")), None)
            if target:
                child_map[e["from"]].append({"node": target, "label": e["label"]})

    levels, visited = {}, set([root["variable"]])
    levels[root["variable"]] = 0
    q = [root["variable"]]
    while q:
        v = q.pop(0)
        for item in child_map.get(v, []):
            nv = item["node"]["variable"]
            if nv not in visited:
                visited.add(nv)
                levels[nv] = levels[v] + 1
                q.append(nv)
    for n in nodes:
        if n["variable"] not in levels:
            levels[n["variable"]] = 0

    by_lvl = {}
    for n in nodes:
        by_lvl.setdefault(levels[n["variable"]], []).append(n["variable"])

    max_lvl   = max(by_lvl.keys())
    max_row_w = max(len(vs) * (NW + HGAP) - HGAP for vs in by_lvl.values())

    pos = {}
    for lvl, vs in by_lvl.items():
        row_w = len(vs) * (NW + HGAP) - HGAP
        off   = (max_row_w - row_w) / 2
        for i, v in enumerate(vs):
            pos[v] = {"x": off + i * (NW + HGAP) + NW / 2,
                      "y": lvl * (NH + VGAP) + NH / 2}

    W = max(max_row_w + 10, 260)
    H = (max_lvl + 1) * (NH + VGAP) + 40

    # Build node data for JS
    import json as _json, html as _html

    def node_color(n):
        is_root  = n.get("role") == "root"
        is_frame = bool(re.search(r'-\d+$', n.get("concept", "")))
        fill  = "#0c447c" if is_root else ("#eaf3de" if is_frame else "#e6f1fb")
        stk   = "#0c447c" if is_root else ("#3b6d11" if is_frame else "#185fa5")
        tv    = "#85b7eb" if is_root else "#888780"
        tc    = "#e6f1fb" if is_root else ("#27500a" if is_frame else "#0c447c")
        return fill, stk, tv, tc

    nodes_js = []
    for n in nodes:
        p = pos.get(n["variable"])
        if not p:
            continue
        fill, stk, tv, tc = node_color(n)
        is_root = n.get("role") == "root"
        concept = n.get("concept", "")
        disp    = concept[:10] + "…" if len(concept) > 11 else concept
        role    = n.get("role", "")
        meaning = n.get("meaning", "")
        nodes_js.append({
            "var": n["variable"], "concept": disp, "fullConcept": concept,
            "role": role, "meaning": meaning,
            "x": p["x"], "y": p["y"],
            "fill": fill, "stk": stk, "tv": tv, "tc": tc,
            "isRoot": is_root
        })

    edges_js = []
    for e in edges:
        fp = pos.get(e.get("from"))
        tp = pos.get(e.get("to"))
        if not fp or not tp:
            continue
        is_re = e.get("is_reentrant", False)
        edges_js.append({
            "from": e.get("from"), "to": e.get("to"),
            "label": e.get("label", ""),
            "x1": fp["x"], "y1": fp["y"] + NH / 2,
            "x2": tp["x"], "y2": tp["y"] - NH / 2,
            "isRe": is_re
        })

    nodes_json = _json.dumps(nodes_js)
    edges_json = _json.dumps(edges_js)

    return f"""
<div style="font-family:'DM Mono',monospace">
<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap">
  <button onclick="startAnimation()" id="btn-play"
    style="font-size:12px;padding:6px 16px;border:0.5px solid #c8c6be;border-radius:6px;
    background:#0f0f0d;color:#f7f5f0;cursor:pointer;font-family:'DM Mono',monospace">
    Play step-by-step
  </button>
  <button onclick="resetGraph()"
    style="font-size:12px;padding:6px 14px;border:0.5px solid #c8c6be;border-radius:6px;
    background:transparent;color:#3a3a35;cursor:pointer;font-family:'DM Mono',monospace">
    Reset
  </button>
  <input type="range" id="speed-slider" min="300" max="2000" value="900" step="100"
    style="width:100px" oninput="updateSpeed(this.value)">
  <span style="font-size:11px;color:#888780" id="speed-label">Speed: medium</span>
</div>

<div id="step-info"
  style="font-size:12px;color:#3a3a35;background:#f7f5f0;border:0.5px solid #e4e0d8;
  border-radius:6px;padding:8px 12px;margin-bottom:10px;min-height:36px;line-height:1.6">
  Press <strong>Play step-by-step</strong> to watch the AMR graph build itself.
</div>

<div style="overflow:auto;background:#fafaf8;border:1px solid #e4e0d8;border-radius:8px;padding:12px">
  <svg id="amr-graph" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="display:block;max-width:100%">
    <defs>
      <marker id="ma" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
        <path d="M1 1.5L8.5 5L1 8.5" fill="none" stroke="#b4b2a9" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </marker>
      <marker id="mr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
        <path d="M1 1.5L8.5 5L1 8.5" fill="none" stroke="#c4501a" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </marker>
    </defs>
    <g id="edges-layer"></g>
    <g id="nodes-layer"></g>
  </svg>
</div>

<div style="display:flex;gap:12px;margin-top:10px;flex-wrap:wrap">
  <div style="display:flex;align-items:center;gap:5px;font-size:11px;color:#7a7a72">
    <rect width="12" height="12" rx="2" style="fill:#0c447c;display:inline-block"></rect>
    <span>Root event</span>
  </div>
  <div style="display:flex;align-items:center;gap:5px;font-size:11px;color:#7a7a72">
    <div style="width:12px;height:12px;border-radius:2px;background:#eaf3de;border:1px solid #3b6d11;display:inline-block"></div>
    <span>PropBank frame</span>
  </div>
  <div style="display:flex;align-items:center;gap:5px;font-size:11px;color:#7a7a72">
    <div style="width:12px;height:12px;border-radius:2px;background:#e6f1fb;border:1px solid #185fa5;display:inline-block"></div>
    <span>Concept</span>
  </div>
  <div style="display:flex;align-items:center;gap:5px;font-size:11px;color:#7a7a72">
    <div style="width:20px;height:2px;background:#c4501a;display:inline-block"></div>
    <span>Coreference</span>
  </div>
</div>
</div>

<script>
(function() {{
  const NW={NW}, NH={NH};
  const nodes = {nodes_json};
  const edges = {edges_json};
  let stepDelay = 900;
  let animTimer = null;
  let running = false;

  function updateSpeed(v) {{
    stepDelay = parseInt(v);
    const labels = {{300:'fast',500:'fast',700:'medium',900:'medium',1200:'slow',1500:'slow',2000:'very slow'}};
    const closest = Object.keys(labels).reduce((a,b) => Math.abs(b-v)<Math.abs(a-v)?b:a);
    document.getElementById('speed-label').textContent = 'Speed: ' + (labels[closest]||'medium');
  }}

  function setInfo(html) {{
    document.getElementById('step-info').innerHTML = html;
  }}

  function resetGraph() {{
    if (animTimer) {{ clearTimeout(animTimer); animTimer=null; running=false; }}
    document.getElementById('edges-layer').innerHTML = '';
    document.getElementById('nodes-layer').innerHTML = '';
    document.getElementById('btn-play').textContent = 'Play step-by-step';
    document.getElementById('btn-play').disabled = false;
    setInfo('Press <strong>Play step-by-step</strong> to watch the AMR graph build itself.');
  }}

  function drawNode(n, highlight) {{
    const g = document.createElementNS('http://www.w3.org/2000/svg','g');
    g.style.opacity = '0';
    g.style.transition = 'opacity 0.5s ease';

    if (n.isRoot) {{
      const crown = document.createElementNS('http://www.w3.org/2000/svg','rect');
      crown.setAttribute('x', n.x-22); crown.setAttribute('y', n.y-NH/2-5);
      crown.setAttribute('width',44); crown.setAttribute('height',6);
      crown.setAttribute('rx',2); crown.setAttribute('fill','#f55036');
      g.appendChild(crown);
    }}

    const rect = document.createElementNS('http://www.w3.org/2000/svg','rect');
    rect.setAttribute('x', n.x-NW/2); rect.setAttribute('y', n.y-NH/2);
    rect.setAttribute('width',NW); rect.setAttribute('height',NH);
    rect.setAttribute('rx',5);
    rect.setAttribute('fill', highlight ? '#fff3b0' : n.fill);
    rect.setAttribute('stroke', highlight ? '#f0b800' : n.stk);
    rect.setAttribute('stroke-width', highlight ? '2' : '0.8');
    rect.style.transition = 'fill 0.6s ease, stroke 0.6s ease';

    const vt = document.createElementNS('http://www.w3.org/2000/svg','text');
    vt.setAttribute('x', n.x-NW/2+6); vt.setAttribute('y', n.y);
    vt.setAttribute('font-size','9'); vt.setAttribute('font-family','DM Mono,monospace');
    vt.setAttribute('fill', n.tv); vt.setAttribute('dominant-baseline','central');
    vt.textContent = n.var + '/';

    const ct = document.createElementNS('http://www.w3.org/2000/svg','text');
    ct.setAttribute('x', n.x+6); ct.setAttribute('y', n.y);
    ct.setAttribute('font-size','11'); ct.setAttribute('font-weight','500');
    ct.setAttribute('font-family','DM Mono,monospace');
    ct.setAttribute('fill', highlight ? '#7a5000' : n.tc);
    ct.setAttribute('text-anchor','middle'); ct.setAttribute('dominant-baseline','central');
    ct.textContent = n.concept;

    g.appendChild(rect); g.appendChild(vt); g.appendChild(ct);
    document.getElementById('nodes-layer').appendChild(g);

    requestAnimationFrame(() => {{ g.style.opacity = '1'; }});

    if (highlight) {{
      setTimeout(() => {{
        rect.setAttribute('fill', n.fill);
        rect.setAttribute('stroke', n.stk);
        ct.setAttribute('fill', n.tc);
      }}, 700);
    }}
    return g;
  }}

  function drawEdgeAnimated(e, cb) {{
    const layer = document.getElementById('edges-layer');
    const is_re = e.isRe;
    const stroke = is_re ? '#c4501a' : '#c8c6be';
    const marker = is_re ? 'url(#mr)' : 'url(#ma)';

    let path;
    let totalLen;

    if (is_re) {{
      const cx = (e.x1+e.x2)/2 + 50;
      const cy = (e.y1+e.y2)/2;
      path = document.createElementNS('http://www.w3.org/2000/svg','path');
      path.setAttribute('d', `M${{e.x1.toFixed(1)}} ${{e.y1.toFixed(1)}} Q${{cx.toFixed(1)}} ${{cy.toFixed(1)}} ${{e.x2.toFixed(1)}} ${{e.y2.toFixed(1)}}`);
      path.setAttribute('fill','none');
      if (is_re) path.setAttribute('stroke-dasharray','5 3');
    }} else {{
      path = document.createElementNS('http://www.w3.org/2000/svg','path');
      path.setAttribute('d', `M${{e.x1.toFixed(1)}} ${{e.y1.toFixed(1)}} L${{e.x2.toFixed(1)}} ${{e.y2.toFixed(1)}}`);
      path.setAttribute('fill','none');
    }}

    path.setAttribute('stroke', stroke);
    path.setAttribute('stroke-width','0.9');
    path.setAttribute('marker-end', marker);
    layer.appendChild(path);

    totalLen = path.getTotalLength ? path.getTotalLength() : 80;
    path.style.strokeDasharray = totalLen;
    path.style.strokeDashoffset = totalLen;
    path.style.transition = `stroke-dashoffset ${{stepDelay*0.7}}ms ease`;

    requestAnimationFrame(() => {{
      path.style.strokeDashoffset = '0';
    }});

    // Label appears after line finishes
    setTimeout(() => {{
      const mx = (e.x1+e.x2)/2 + (is_re ? 26 : 4);
      const my = (e.y1+e.y2)/2 - 3;
      const t = document.createElementNS('http://www.w3.org/2000/svg','text');
      t.setAttribute('x', mx); t.setAttribute('y', my);
      t.setAttribute('font-size','9'); t.setAttribute('font-family','DM Mono,monospace');
      t.setAttribute('fill', is_re ? '#c4501a' : '#888780');
      t.setAttribute('text-anchor','middle');
      t.style.opacity = '0';
      t.style.transition = 'opacity 0.4s ease';
      t.textContent = e.label;
      layer.appendChild(t);
      requestAnimationFrame(() => {{ t.style.opacity = '1'; }});
      if (cb) cb();
    }}, stepDelay * 0.75);
  }}

  window.startAnimation = function() {{
    if (running) return;
    resetGraph();
    running = true;
    document.getElementById('btn-play').textContent = 'Building…';
    document.getElementById('btn-play').disabled = true;

    // Build step list: root first, then nodes by level, then edges
    const rootNode = nodes.find(n => n.isRoot) || nodes[0];
    const otherNodes = nodes.filter(n => !n.isRoot);
    const steps = [];

    // Step 0: root
    steps.push({{
      type:'node', data: rootNode,
      info: `<strong>Step 1 — Root node</strong><br>
             <span style="font-family:monospace;color:#0c447c">${{rootNode.var}} / ${{rootNode.fullConcept}}</span><br>
             The main event of the sentence. Everything else attaches to this.`
    }});

    // Subsequent nodes
    otherNodes.forEach((n, i) => {{
      const roleText = n.role === 'root' ? '' : ` via <span style="font-family:monospace;color:#854F0B">${{n.role}}</span>`;
      steps.push({{
        type:'node', data: n,
        info: `<strong>Node ${{i+2}}</strong>${{roleText}}<br>
               <span style="font-family:monospace;color:#0c447c">${{n.var}} / ${{n.fullConcept}}</span><br>
               ${{n.meaning}}`
      }});
    }});

    // Edges
    edges.forEach((e, i) => {{
      const fromNode = nodes.find(n => n.var === e.from);
      const toNode   = nodes.find(n => n.var === e.to);
      const fn = fromNode ? fromNode.fullConcept : e.from;
      const tn = toNode   ? toNode.fullConcept   : e.to;
      const reText = e.isRe ? ' <em>(coreference — same node referenced again)</em>' : '';
      steps.push({{
        type:'edge', data: e,
        info: `<strong>Edge — <span style="font-family:monospace;color:#854F0B">${{e.label}}</span></strong>${{reText}}<br>
               <span style="font-family:monospace">${{fn}}</span> →
               <span style="font-family:monospace">${{tn}}</span><br>
               ${{e.label === ':ARG0' ? 'Agent: who performs the action' :
                  e.label === ':ARG1' ? 'Patient: what the action is done to' :
                  e.label === ':ARG2' ? 'Destination or beneficiary' :
                  e.label === ':mod'  ? 'Modifier: describes a property' :
                  e.label === ':polarity' ? 'Negation: this event did NOT happen' :
                  e.label === ':name' ? 'Name: labels a named entity' :
                  e.label === ':quant'? 'Quantity: how many' :
                  'Semantic relation between concepts'}}`
      }});
    }});

    // Final step
    steps.push({{
      type:'done',
      info: `<strong>Graph complete!</strong><br>
             ${{nodes.length}} nodes · ${{edges.length}} edges · This is the full AMR.`
    }});

    let si = 0;
    function runStep() {{
      if (si >= steps.length) {{
        running = false;
        document.getElementById('btn-play').textContent = 'Play again';
        document.getElementById('btn-play').disabled = false;
        return;
      }}
      const step = steps[si++];
      setInfo(step.info);

      if (step.type === 'node') {{
        drawNode(step.data, true);
        animTimer = setTimeout(runStep, stepDelay);
      }} else if (step.type === 'edge') {{
        drawEdgeAnimated(step.data, () => {{
          animTimer = setTimeout(runStep, stepDelay * 0.3);
        }});
      }} else {{
        animTimer = setTimeout(runStep, stepDelay);
      }}
    }}
    runStep();
  }};

  window.resetGraph = resetGraph;
  window.updateSpeed = updateSpeed;
}})();
</script>
"""


# ── AMR syntax highlighter ──────────────────────────────────────────────────
def highlight_amr(raw: str) -> str:
    import html as h
    s = h.escape(raw)
    s = re.sub(r'\b([a-z][a-z0-9]*)\s*(\/)',
               r'<span class="amr-var">\1</span> \2', s)
    s = re.sub(r'(/\s+)([a-zA-Z0-9_-]+)',
               lambda m: m.group(1) + f'<span class="amr-concept">{m.group(2)}</span>', s)
    s = re.sub(r'(:[A-Za-z0-9_-]+)', r'<span class="amr-role">\1</span>', s)
    s = re.sub(r'"([^"]*)"',          r'<span class="amr-lit">"\1"</span>', s)
    return s



# ── Deep explanation renderer ───────────────────────────────────────────────
def render_deep_explanation(d: dict):
    de = d.get("deep_explanation")
    if not de:
        return

    st.markdown('<div class="section-label">Deep explanation</div>', unsafe_allow_html=True)
    st.markdown('<div class="deep-wrap">', unsafe_allow_html=True)

    # 1 — Plain English summary
    if de.get("summary"):
        st.markdown(f"""
        <div class="deep-card">
          <div class="deep-card-head"><div class="deep-dot" style="background:#f55036"></div>What this sentence means</div>
          <div class="deep-card-body">
            <div class="deep-summary">{de["summary"]}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    # 2 — Root concept explained
    rc = de.get("root_concept", {})
    if rc:
        st.markdown(f"""
        <div class="deep-card">
          <div class="deep-card-head"><div class="deep-dot" style="background:#1a4a6b"></div>Root concept — why <code>{rc.get("concept","")}</code> is the centre</div>
          <div class="deep-card-body">
            <div class="deep-text">{rc.get("why_root","")}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    # 3 — Roles explained
    roles = de.get("roles_explained", [])
    if roles:
        rows_html = ""
        for r in roles:
            rows_html += f"""
            <div class="role-row">
              <span class="role-pill">{r.get("role","")}</span>
              <span class="role-concept">{r.get("concept","")}</span>
              <span class="role-desc">{r.get("plain_english","")}</span>
            </div>"""
        st.markdown(f"""
        <div class="deep-card">
          <div class="deep-card-head"><div class="deep-dot" style="background:#c4501a"></div>Semantic roles — who does what to whom</div>
          <div class="deep-card-body">{rows_html}</div>
        </div>""", unsafe_allow_html=True)

    # 4 — Special features
    features = de.get("special_features", [])
    if features:
        feat_html = ""
        for f in features:
            feat_html += f"""
            <div class="feature-row">
              <span class="feature-tag">{f.get("feature","")}</span>
              <span class="role-desc">{f.get("detail","")}</span>
            </div>"""
        st.markdown(f"""
        <div class="deep-card">
          <div class="deep-card-head"><div class="deep-dot" style="background:#854F0B"></div>Special AMR features in this sentence</div>
          <div class="deep-card-body">{feat_html}</div>
        </div>""", unsafe_allow_html=True)

    # 5 — What AMR ignores
    if de.get("what_amr_ignores"):
        st.markdown(f"""
        <div class="deep-card">
          <div class="deep-card-head"><div class="deep-dot" style="background:#888780"></div>What AMR deliberately ignores</div>
          <div class="deep-card-body">
            <div class="ignore-box">{de["what_amr_ignores"]}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    # 6 — PropBank note
    if de.get("propbank_note"):
        st.markdown(f"""
        <div class="deep-card">
          <div class="deep-card-head"><div class="deep-dot" style="background:#1a6b4a"></div>PropBank frames used</div>
          <div class="deep-card-body">
            <div class="propbank-box">{de["propbank_note"]}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ── Main input ──────────────────────────────────────────────────────────────
if "sentence" not in st.session_state:
    st.session_state["sentence"] = ""

# Keep input box in sync when a suggestion is clicked
if st.session_state.get("sentence") and st.session_state.get("sentence") != st.session_state.get("sentence_input", ""):
    st.session_state["sentence_input"] = st.session_state["sentence"]

col_inp, col_btn = st.columns([5, 1])
with col_inp:
    sentence = st.text_input(
        "sentence",
        placeholder="Type in English, Hindi (हिंदी), Kannada (ಕನ್ನಡ), Telugu (తెలుగు), Tamil (தமிழ்)...",
        label_visibility="collapsed",
        key="sentence_input",
    )
with col_btn:
    parse_clicked = st.button("Parse →", use_container_width=True)

# Auto-parse when a suggestion chip was clicked
if st.session_state.get("_auto_parse"):
    st.session_state["_auto_parse"] = False
    parse_clicked = True


# ── Parse ───────────────────────────────────────────────────────────────────
if parse_clicked and sentence.strip():
    if not api_key:
        st.error("Please enter your Groq API key in the sidebar. Get one free at console.groq.com")
    else:
        with st.spinner("Groq is parsing the semantic structure…"):
            try:
                raw_text = call_groq(api_key, build_prompt(sentence))
                data     = safe_parse(raw_text)
                st.session_state["amr_result"]   = data
                st.session_state["amr_sentence"]  = sentence
                # Fetch smart suggestions in the background
                sugg = fetch_suggestions(api_key, sentence, data.get("nodes", []))
                st.session_state["suggestions"]   = sugg
            except json.JSONDecodeError as e:
                st.error(f"Could not parse response as JSON. Try again. Detail: {e}")
            except Exception as e:
                st.error(f"Error: {e}")


# ── Results ─────────────────────────────────────────────────────────────────
if "amr_result" in st.session_state:
    data = st.session_state["amr_result"]

    if data.get("is_nonsense"):
        st.markdown(
            '<div class="nonsense-banner"><strong>Unclear input</strong> — '
            'does not appear to be a valid sentence. Showing best-effort AMR.</div>',
            unsafe_allow_html=True,
        )

    # Language detection banner
    lang = data.get("detected_language", "English")
    is_english = data.get("is_english", True)
    if not is_english:
        translation   = data.get("translation", "")
        translit      = data.get("transliteration", "")
        translit_html = f'<br><span style="opacity:.7">Pronunciation: <em>{translit}</em></span>' if translit else ""
        st.markdown(
            f'<div class="lang-banner">'
            f'<strong>Language detected: {lang}</strong><br>'
            f'Translation: <em>{translation}</em>'
            f'{translit_html}<br>'
            f'<span style="opacity:.7;font-size:0.75rem">AMR is built from the English translation</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    elif data.get("has_spelling_errors") and data.get("spelling_changes"):
        changes = " &nbsp;·&nbsp; ".join(data["spelling_changes"])
        st.markdown(
            f'<div class="spell-banner"><strong>Spelling corrected</strong> — '
            f'AMR built from corrected sentence.<br>'
            f'Changes: <strong>{changes}</strong><br>'
            f'<span style="opacity:.75">Corrected: "{data.get("corrected","")}"</span></div>',
            unsafe_allow_html=True,
        )

    # Show original (and translation if non-English)
    display_sent = data.get("corrected") or data.get("translation") or data.get("original", sentence)
    original_raw = data.get("original", "")
    if not is_english and original_raw:
        st.markdown(f'<div class="expl-sentence">{original_raw}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:0.82rem;color:#7a7a72;margin-bottom:0.4rem;font-style:italic">English: "{display_sent}"</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="expl-sentence">"{display_sent}"</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="expl-text">{data.get("explanation","")}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_amr, col_graph = st.columns(2)
    with col_amr:
        st.markdown('<div class="section-label">AMR notation</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="amr-block">{highlight_amr(data.get("amr_notation",""))}</div>',
            unsafe_allow_html=True,
        )
    with col_graph:
        st.markdown('<div class="section-label">Graph — animated</div>', unsafe_allow_html=True)
        animated_html = build_animated_graph(data.get("nodes", []), data.get("edges", []))
        if animated_html:
            graph_h = max(340, len(data.get("nodes",[])) * 90 + 200)
            components.html(animated_html, height=graph_h, scrolling=False)

    # Word map (for non-English input)
    word_map = data.get("word_map", [])
    if word_map and not is_english:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Word-by-word mapping</div>', unsafe_allow_html=True)
        wm_rows = ""
        for w in word_map:
            src  = w.get("source_word", "")
            trl  = w.get("translation", "")
            role = w.get("amr_role", "")
            note = w.get("note", "")
            wm_rows += (
                f'<tr>'
                f'<td><span class="src-word">{src}</span></td>'
                f'<td>{trl}</td>'
                f'<td><span class="role-badge">{role}</span></td>'
                f'<td style="color:#7a7a72">{note}</td>'
                f'</tr>'
            )
        st.markdown(
            f'<table class="word-map-table"><thead><tr>'
            f'<th>{lang} word</th><th>English</th><th>AMR role</th><th>Note</th>'
            f'</tr></thead><tbody>{wm_rows}</tbody></table>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Node &amp; edge breakdown</div>', unsafe_allow_html=True)
    rows = "".join(
        f'<tr>'
        f'<td><span class="var-badge">{n.get("variable","")}</span></td>'
        f'<td><span class="con-badge">{n.get("concept","")}</span></td>'
        f'<td><span class="role-badge">{n.get("role","")}</span></td>'
        f'<td>{n.get("meaning","")}</td>'
        f'</tr>'
        for n in data.get("nodes", [])
    )
    st.markdown(
        f'<table class="node-table"><thead><tr>'
        f'<th>Variable</th><th>Concept</th><th>Role</th><th>Meaning</th>'
        f'</tr></thead><tbody>{rows}</tbody></table>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    render_deep_explanation(data)

    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label="Download AMR JSON",
        data=json.dumps(data, indent=2),
        file_name="amr_result.json",
        mime="application/json",
    )

elif not parse_clicked:
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem;color:#7a7a72;font-size:0.82rem;line-height:2.2">
        Enter a sentence above and click <strong>Parse →</strong><br>
        Supports <strong>English · Hindi · Kannada · Telugu · Tamil</strong> and more.<br>
        AMR captures <em>who did what to whom</em>, ignoring word order and tense.<br>
        <span style="font-size:0.72rem;color:#aaa">Powered by Groq · Llama 3.3 70B · Free forever</span>
    </div>
    """, unsafe_allow_html=True)
