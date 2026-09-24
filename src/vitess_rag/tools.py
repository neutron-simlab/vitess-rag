import re

from langchain.tools import tool

from .retrieval import (
    build_context,
    detect_ambiguity,
    rerank_results,
    retrieve_candidates,
)


def create_vitess_tools(collection):
    @tool
    def vitess_search(query: str) -> str:
        """
        General search over VITESS documentation.
        Use this for broad questions, explanations, and module descriptions.
        """
        docs, metas = retrieve_candidates(query, collection, n_results=30)

        if not docs:
            return "NO_RESULTS"

        ranked = rerank_results(query, docs, metas)

        ambiguity = detect_ambiguity(query, ranked)
        if ambiguity:
            return f"AMBIGUOUS_QUERY\n{ambiguity}"

        return build_context(ranked[:5])

    @tool
    def vitess_option_lookup(query: str) -> str:
        """
        Specialized lookup for command-line options like -z, -A, -H, -V.
        Use this when the user asks what an option means.
        """

        target_option = re.search(r"-[A-Za-z]", query)

        if not target_option:
            return "NO_OPTION_FOUND"

        option = target_option.group(0)

        # First, perform an exact lookup over indexed metadata.
        results = collection.get(
            include=["documents", "metadatas"],
        )

        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])

        exact_hits = []

        for doc, meta in zip(documents, metadatas):
            row_cmd = str(meta.get("row_command_option", "")).strip()

            if not row_cmd:
                continue

            options_in_row = re.findall(r"-[A-Za-z]", row_cmd)

            if option in options_in_row:
                exact_hits.append((0, meta, doc))

        if exact_hits:
            exact_docs = [doc for _, _, doc in exact_hits]
            exact_metas = [meta for _, meta, _ in exact_hits]

            ranked = rerank_results(
                query,
                exact_docs,
                exact_metas,
            )

            ambiguity = detect_ambiguity(query, ranked)

            if ambiguity:
                return f"AMBIGUOUS_QUERY\n{ambiguity}"

            return build_context(ranked[:5])

        # Fallback: use semantic retrieval if no exact option match was found.
        docs, metas = retrieve_candidates(
            query,
            collection,
            n_results=50,
        )

        if not docs:
            return "NO_RESULTS"

        ranked = rerank_results(query, docs, metas)

        ambiguity = detect_ambiguity(query, ranked)

        if ambiguity:
            return f"AMBIGUOUS_QUERY\n{ambiguity}"

        return build_context(ranked[:5])


    @tool
    def vitess_module_lookup(query: str) -> str:
        """
        Focused lookup for questions about one module or one section,
        such as 'explain guide ideal' or 'what is filter2D'.
        """
        docs, metas = retrieve_candidates(query, collection, n_results=30)

        if not docs:
            return "NO_RESULTS"

        ranked = rerank_results(query, docs, metas)

        _, best_meta, _ = ranked[0]

        module = str(best_meta.get("module", "") or "")
        section = str(best_meta.get("section", "") or "")
        subsection = str(best_meta.get("subsection", "") or "")
        subsubsection = str(best_meta.get("subsubsection", "") or "")

        focused = []

        for score, meta, doc in ranked:
            same_module = str(meta.get("module", "") or "") == module

            if not same_module:
                continue

            if section and str(meta.get("section", "") or "") != section:
                continue

            if subsection and str(meta.get("subsection", "") or "") != subsection:
                continue

            if subsubsection and str(meta.get("subsubsection", "") or "") != subsubsection:
                continue

            focused.append((score, meta, doc))

        if focused:
            return build_context(focused[:8])

        return build_context(ranked[:5])

    @tool
    def vitess_debug_retrieval(query: str) -> str:
        """
        Debug tool. Shows the top retrieved chunks and scores.
        Use only if the answer seems uncertain or retrieval may be wrong.
        """
        docs, metas = retrieve_candidates(query, collection, n_results=10)

        if not docs:
            return "NO_RESULTS"

        ranked = rerank_results(query, docs, metas)

        lines = []

        for i, (score, meta, doc) in enumerate(ranked[:10], 1):
            lines.append(
                f"""[{i}]
score: {score}
module: {meta.get("module", "")}
section: {meta.get("section", "")}
subsection: {meta.get("subsection", "")}
chunk_type: {meta.get("chunk_type", "")}
row_command_option: {meta.get("row_command_option", "")}
row_parameter_unit: {meta.get("row_parameter_unit", "")}
snippet: {str(doc)[:300]}"""
            )

        return "\n\n".join(lines)

    return [
        vitess_search,
        vitess_option_lookup,
        vitess_module_lookup,
        vitess_debug_retrieval,
    ]
