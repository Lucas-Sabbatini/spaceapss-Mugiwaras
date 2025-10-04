import re

# Reduzimos a lista para os únicos cabeçalhos que nos interessam
ABSTRACT_HEADERS = [
    ("abstract", r"^\s*(\d+\.?\s*)?(abstract)\b"),
    ("introduction", r"^\s*(\d+\.?\s*)?(introduction|background)\b"),
]

def sectionize_text(text: str):
    """
    Versão simplificada: Procura pelo abstract ou introdução e agrupa todo o resto como 'content'.
    Retorna um dicionário com as chaves 'abstract' e 'content'.
    """
    if not text or not text.strip():
        return {"abstract": "", "content": ""}

    # Divide o texto em blocos (parágrafos)
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
    if cur:
        blocks.append("\n".join(cur).strip())

    if not blocks:
        return {"abstract": "", "content": ""}

    header_index = -1
    abstract_header_name = None

    # Procura pelo índice do primeiro cabeçalho que corresponde a abstract ou introduction
    for i, block in enumerate(blocks):
        first_line = block.splitlines()[0][:120].lower()
        for name, rx in ABSTRACT_HEADERS:
            if re.match(rx, first_line):
                header_index = i
                abstract_header_name = name
                break
        if header_index != -1:
            break
    
    abstract_text = ""
    content_text = ""
    
    # Se encontrámos um cabeçalho e há texto a seguir...
    if header_index != -1 and (header_index + 1) < len(blocks):
        # O bloco de texto a seguir ao cabeçalho é o nosso abstract
        abstract_text = blocks[header_index + 1]
        # Todo o resto (antes do cabeçalho e depois do abstract) é o conteúdo
        content_blocks = blocks[:header_index] + blocks[header_index+2:]
        content_text = "\n\n".join(content_blocks)
    else:
        # Fallback: se não encontrámos cabeçalho, o primeiro bloco é o abstract
        # e o resto é o conteúdo.
        abstract_text = blocks[0]
        content_text = "\n\n".join(blocks[1:])

    return {"abstract": abstract_text.strip(), "content": content_text.strip()}