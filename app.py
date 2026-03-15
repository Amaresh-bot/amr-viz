import streamlit as st
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
                    st.rerun()

        # Contrast sentences
        contrast = sugg.get("contrast", [])
        if contrast:
            st.markdown("**See the contrast**")
            for s in contrast:
                if st.button(s, key=f"sugg_con_{s[:30]}"):
                    st.session_state["sentence"] = s
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
                        st.rerun()

        st.markdown("---")

    # ── Static examples (always shown) ─────────────────────────────────────
    st.markdown("**Example sentences**")
    examples = [
        "The boy wants to go.",
        "She did not believe him.",
        "Obama went to Paris.",
        "He wants her to stop crying.",
        "The company fired fifty workers.",
        "teh cat sat on teh mat",
        "She rekognized hiz face.",
        "The girl quickly ran to school.",
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex}"):
            st.session_state["sentence"] = ex
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
    return f"""You are an AMR (Abstract Meaning Representation) expert and spelling corrector.

INPUT SENTENCE: "{sentence}"

STEP 1 — Check for spelling mistakes. Correct any typos silently.
STEP 2 — Produce a complete AMR for the corrected sentence.
STEP 3 — Write a rich explanation as described below.

Return ONLY a raw JSON object. No markdown fences. No text before or after the JSON.

{{
  "original": "exactly as typed by user",
  "corrected": "spell-corrected version, same as original if no errors",
  "has_spelling_errors": true or false,
  "spelling_changes": ["teh -> the"] or [],
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
    "special_features": [
      {{
        "feature": "Coreference",
        "detail": "Variable b appears twice — AMR reuses it to show the boy is both the wanter and the goer, avoiding repetition."
      }}
    ],
    "what_amr_ignores": "AMR ignores tense, articles (the/a), and word order. It only captures core meaning.",
    "propbank_note": "want-01 comes from PropBank — a dictionary of verb senses. The -01 means sense 1 of want."
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
- PropBank frames only (want-01, go-02, believe-01, discover-01, etc.)
- Variables: single lowercase letters only
- meaning: 5 words max
- explanation and all deep_explanation strings: no double-quotes inside any string value
- special_features: list only features that actually appear (negation, coreference, named entities, modifiers, quantifiers). Empty list [] if none.
- is_reentrant: true only for coreference (same variable referenced twice)
- Root node role must be exactly "root"
- For negation: node with variable "neg", concept "-", role ":polarity"
- Named entities: person/city/country concept + :name + :op1 "String"
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
    """Remove control characters and fix common JSON issues from LLM output."""
    # Strip markdown fences
    text = re.sub(r'^```(?:json)?\s*', '', text.strip(), flags=re.I)
    text = re.sub(r'\s*```$', '', text.strip())
    # Extract just the JSON object
    f, l = text.find("{"), text.rfind("}")
    if f != -1 and l > f:
        text = text[f:l+1]
    # Fix control characters inside JSON strings — the main cause of this error.
    # Walk char by char: inside a string, replace raw newlines/tabs with escape sequences.
    result = []
    in_string = False
    escape_next = False
    for ch in text:
        if escape_next:
            result.append(ch)
            escape_next = False
            continue
        if ch == '\\':
            result.append(ch)
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            result.append(ch)
            continue
        if in_string:
            if ch == '\n':
                result.append('\\n')
            elif ch == '\r':
                result.append('\\r')
            elif ch == '\t':
                result.append('\\t')
            elif ord(ch) < 32:
                # Replace any other control character with a space
                result.append(' ')
            else:
                result.append(ch)
        else:
            result.append(ch)
    return ''.join(result)

def safe_parse(text: str) -> dict:
    text = clean_json_string(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Last resort: close any unclosed structures
        r = text.rstrip().rstrip(",")
        if r.count('"') % 2 != 0:
            r += '"'
        r += "]" * max(0, r.count("[") - r.count("]"))
        r += "}" * max(0, r.count("{") - r.count("}"))
        return json.loads(r)


# ── SVG graph builder ───────────────────────────────────────────────────────
def build_svg(nodes: list, edges: list) -> str:
    if not nodes:
        return ""

    NW, NH, HGAP, VGAP = 118, 34, 24, 66
    root = next((n for n in nodes if n.get("role") == "root"), nodes[0])

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

    max_lvl    = max(by_lvl.keys())
    max_row_w  = max(len(vs) * (NW + HGAP) - HGAP for vs in by_lvl.values())

    pos = {}
    for lvl, vs in by_lvl.items():
        row_w = len(vs) * (NW + HGAP) - HGAP
        off   = (max_row_w - row_w) / 2
        for i, v in enumerate(vs):
            pos[v] = {"x": off + i * (NW + HGAP) + NW / 2,
                      "y": lvl * (NH + VGAP) + NH / 2}

    W = max(max_row_w + 10, 260)
    H = (max_lvl + 1) * (NH + VGAP) + 30

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" style="display:block;max-width:100%">',
        """<defs>
  <marker id="ma" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
    <path d="M1 1.5L8.5 5L1 8.5" fill="none" stroke="#b4b2a9" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
  <marker id="mr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
    <path d="M1 1.5L8.5 5L1 8.5" fill="none" stroke="#c4501a" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
</defs>"""
    ]

    for e in edges:
        fp = pos.get(e.get("from"))
        tp = pos.get(e.get("to"))
        if not fp or not tp:
            continue
        is_re  = e.get("is_reentrant", False)
        x1, y1 = fp["x"], fp["y"] + NH / 2
        x2, y2 = tp["x"], tp["y"] - NH / 2
        stroke  = "#c4501a" if is_re else "#c8c6be"
        dash    = 'stroke-dasharray="5 3"' if is_re else ""
        marker  = "url(#mr)" if is_re else "url(#ma)"
        if is_re:
            cx = (x1 + x2) / 2 + 50
            parts.append(
                f'<path d="M{x1:.1f} {y1:.1f} Q{cx:.1f} {(y1+y2)/2:.1f} {x2:.1f} {y2:.1f}" '
                f'fill="none" stroke="{stroke}" stroke-width="0.9" {dash} marker-end="{marker}"/>'
            )
        else:
            parts.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{stroke}" stroke-width="0.9" marker-end="{marker}"/>'
            )
        mx = (x1 + x2) / 2 + (26 if is_re else 4)
        my = (y1 + y2) / 2 - 3
        lc  = "#c4501a" if is_re else "#888780"
        parts.append(
            f'<text x="{mx:.1f}" y="{my:.1f}" font-size="9" font-family="DM Mono,monospace" '
            f'fill="{lc}" text-anchor="middle">{e.get("label","")}</text>'
        )

    for n in nodes:
        p = pos.get(n["variable"])
        if not p:
            continue
        is_root  = n.get("role") == "root"
        rx, ry   = p["x"] - NW / 2, p["y"] - NH / 2
        is_frame = bool(re.search(r'-\d+$', n.get("concept", "")))
        fill     = "#0c447c" if is_root else ("#eaf3de" if is_frame else "#e6f1fb")
        stk      = "#0c447c" if is_root else ("#3b6d11" if is_frame else "#185fa5")
        tv       = "#85b7eb" if is_root else "#888780"
        tc       = "#e6f1fb" if is_root else ("#27500a" if is_frame else "#0c447c")
        concept  = n.get("concept", "")
        disp     = concept[:10] + "…" if len(concept) > 11 else concept

        if is_root:
            parts.append(
                f'<rect x="{p["x"]-22:.1f}" y="{ry-5:.1f}" width="44" height="6" rx="2" fill="#f55036"/>'
            )
        parts.append(
            f'<rect x="{rx:.1f}" y="{ry:.1f}" width="{NW}" height="{NH}" rx="5" '
            f'fill="{fill}" stroke="{stk}" stroke-width="0.8"/>'
        )
        parts.append(
            f'<text x="{rx+6:.1f}" y="{p["y"]:.1f}" font-size="9" font-family="DM Mono,monospace" '
            f'fill="{tv}" dominant-baseline="central">{n["variable"]}/</text>'
        )
        parts.append(
            f'<text x="{p["x"]+6:.1f}" y="{p["y"]:.1f}" font-size="11" font-weight="500" '
            f'font-family="DM Mono,monospace" fill="{tc}" text-anchor="middle" '
            f'dominant-baseline="central">{disp}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


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

col_inp, col_btn = st.columns([5, 1])
with col_inp:
    sentence = st.text_input(
        "sentence",
        value=st.session_state["sentence"],
        placeholder="e.g. The scientist quickly discovered a cure.",
        label_visibility="collapsed",
        key="sentence_input",
    )
with col_btn:
    parse_clicked = st.button("Parse →", use_container_width=True)


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
    elif data.get("has_spelling_errors") and data.get("spelling_changes"):
        changes = " &nbsp;·&nbsp; ".join(data["spelling_changes"])
        st.markdown(
            f'<div class="spell-banner"><strong>Spelling corrected</strong> — '
            f'AMR built from corrected sentence.<br>'
            f'Changes: <strong>{changes}</strong><br>'
            f'<span style="opacity:.75">Corrected: "{data.get("corrected","")}"</span></div>',
            unsafe_allow_html=True,
        )

    display_sent = data.get("corrected") or data.get("original", sentence)
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
        st.markdown('<div class="section-label">Graph</div>', unsafe_allow_html=True)
        svg = build_svg(data.get("nodes", []), data.get("edges", []))
        if svg:
            st.markdown(
                f'<div style="border:1px solid #e4e0d8;border-radius:8px;padding:14px;'
                f'background:#fafaf8;overflow:auto">{svg}</div>',
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
        AMR captures <em>who did what to whom</em>, ignoring word order and tense.<br>
        Spelling mistakes are detected and corrected automatically.<br>
        <span style="font-size:0.72rem;color:#aaa">Powered by Groq · Llama 3.3 70B · Free forever</span>
    </div>
    """, unsafe_allow_html=True)

