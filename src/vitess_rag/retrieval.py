import re
from typing import Any, Optional


def normalize_text(s: Any) -> str:
    return re.sub(r"\s+", " ", str(s).lower()).strip()


def extract_command_option(query: str) -> Optional[str]:
    match = re.search(r"-[A-Za-z]", query)
    return match.group(0) if match else None


def extract_module_hint(query: str, metas) -> Optional[str]:
    q = query.lower()

    stopwords = {
        "vitess", "module", "modules",
        "section", "subsection", "subsubsection",
        "table", "tables", "following", "lists", "list",
        "parameters", "parameter",
        "information", "file", "files",
        "input", "inputs", "output", "outputs",
        "data", "values", "value",
        "description", "range", "option", "options",
        "what", "does", "mean", "show", "tell", "about",
        "from", "with", "into", "that", "this", "these", "those",
    }

    candidates = set()

    for meta in metas:
        for field in ["module", "section", "subsection", "subsubsection", "source_file", "path"]:
            text = str(meta.get(field, "")).lower()
            words = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", text)

            for word in words:
                if len(word) > 3 and word not in stopwords:
                    candidates.add(word)

    for candidate in sorted(candidates, key=len, reverse=True):
        if re.search(rf"\b{re.escape(candidate)}\b", q):
            return candidate

    return None


def has_module_hint(query: str, metas) -> bool:
    return extract_module_hint(query, metas) is not None


def retrieve_candidates(query: str, collection, n_results: int = 20):
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )
    return results["documents"][0], results["metadatas"][0]


def rerank_results(query: str, docs, metas):
    q = normalize_text(query)
    target_option = extract_command_option(query)
    module_hint = extract_module_hint(query, metas)

    scored = []

    for rank, (doc, meta) in enumerate(zip(docs, metas)):
        score = -rank
        text = normalize_text(doc)

        module = normalize_text(meta.get("module", ""))
        section = normalize_text(meta.get("section", ""))
        subsection = normalize_text(meta.get("subsection", ""))
        subsubsection = normalize_text(meta.get("subsubsection", ""))
        source_file = normalize_text(meta.get("source_file", ""))
        path = normalize_text(meta.get("path", ""))
        chunk_type = str(meta.get("chunk_type", ""))

        row_cmd = str(meta.get("row_command_option", "")).strip()
        row_cmd_norm = normalize_text(row_cmd)
        row_options = re.findall(r"-[A-Za-z]", row_cmd)

        if target_option and row_cmd == target_option:
            score += 100

        if target_option and target_option in row_options:
            score += 80

        if target_option and target_option.lower() in text:
            score += 20

        if module_hint:
            in_same_context = (
                module_hint in module
                or module_hint in section
                or module_hint in subsection
                or module_hint in subsubsection
                or module_hint in source_file
                or module_hint in path
                or module_hint in text
            )

            if in_same_context:
                score += 40
            elif target_option and (row_cmd == target_option or target_option in row_options):
                score -= 25

        if chunk_type == "table":
            score += 5

        if ("what does option" in q or "option" in q or "parameter" in q) and row_cmd_norm:
            score += 5

        if module_hint == "bender" and "information file" in subsection:
            score += 8

        scored.append((score, meta, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored


def format_ambiguous_matches(
    target_option: str,
    exact_matches,
    max_items: int = 10,
) -> str:
    lines = [
        f"The option **{target_option}** is used in multiple places, "
        "so its meaning depends on the VITESS module:\n"
    ]

    seen = set()
    count = 0

    for _, meta, _ in exact_matches:
        module = meta.get("module", "") or "Unknown module"
        parameter = (
            meta.get("row_parameter_unit", "")
            or "Unknown parameter"
        )
        description = (
            meta.get("row_description", "")
            or "No description available."
        )

        key = (module, parameter, description)

        if key in seen:
            continue

        seen.add(key)

        lines.append(
            f"- **{module}**: **{parameter}** — {description}"
        )

        count += 1

        if count >= max_items:
            break

    lines.append(
        f"\nPlease specify the module for **{target_option}** "
        "so I can give the precise definition."
    )

    return "\n".join(lines)


def detect_ambiguity(query: str, ranked):
    target_option = extract_command_option(query)

    if not target_option:
        return None

    ranked_metas = [meta for _, meta, _ in ranked]

    if has_module_hint(query, ranked_metas):
        return None

    exact_matches = []

    for score, meta, doc in ranked:
        row_cmd = str(meta.get("row_command_option", "")).strip()
        options_in_row = re.findall(r"-[A-Za-z]", row_cmd)

        if target_option in options_in_row:
            exact_matches.append((score, meta, doc))

    unique = []
    seen = set()

    for item in exact_matches:
        _, meta, _ = item
        key = (
            meta.get("module", ""),
            meta.get("row_parameter_unit", ""),
            meta.get("row_description", ""),
        )

        if key not in seen:
            seen.add(key)
            unique.append(item)

    unique_modules = {
        meta.get("module", "") or "Unknown module"
        for _, meta, _ in unique
    }

    if len(unique_modules) > 1:
        return format_ambiguous_matches(target_option, unique)

    return None


def build_context(top_hits) -> str:
    blocks = []

    for i, (score, meta, doc) in enumerate(top_hits, 1):
        blocks.append(
            f"""[Chunk {i}]
score: {score}
module: {meta.get("module", "")}
section: {meta.get("section", "")}
subsection: {meta.get("subsection", "")}
subsubsection: {meta.get("subsubsection", "")}
chunk_type: {meta.get("chunk_type", "")}
row_parameter_unit: {meta.get("row_parameter_unit", "")}
row_command_option: {meta.get("row_command_option", "")}
row_description: {meta.get("row_description", "")}
table_title: {meta.get("table_title", "")}
table_descriptor: {meta.get("table_descriptor", "")}
source_file: {meta.get("source_file", "")}
path: {meta.get("path", "")}
content: {doc}"""
        )

    return "\n\n".join(blocks)
