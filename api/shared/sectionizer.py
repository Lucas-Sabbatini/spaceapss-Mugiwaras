import re

HEADERS = [
    ("introduction", r"^\s*(introduction|background)\b"),
    ("methods", r"^\s*(methods?|materials and methods?)\b"),
    ("results", r"^\s*(results?)\b"),
    ("discussion", r"^\s*(discussion)\b"),
    ("conclusion", r"^\s*(conclusions?)\b"),
]

def sectionize_text(text: str):
    if not text: 
        return {"other": ""}
    lines = text.splitlines()
    blocks = []
    cur = []
    for ln in lines:
        if ln.strip():
            cur.append(ln)
        else:
            if cur:
                blocks.append("\n".join(cur).strip())
                cur = []
    if cur: blocks.append("\n".join(cur).strip())

    sections = {"introduction":"", "methods":"", "results":"", "discussion":"", "conclusion":"", "other":""}
    current = "other"
    for b in blocks:
        header = detect_header(b)
        if header:
            current = header
            sections.setdefault(current, "")
            continue
        sections[current] = (sections[current] + "\n\n" + b).strip()
    return sections

def detect_header(block: str):
    first = block.splitlines()[0][:120].lower()
    for name, rx in HEADERS:
        if re.match(rx, first):
            return name
    return None
