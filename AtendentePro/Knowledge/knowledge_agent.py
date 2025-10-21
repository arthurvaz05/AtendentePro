from __future__ import annotations

import logging
import pathlib
import pickle
import sys

from pydantic import BaseModel, Field

try:
    from agents import Agent, function_tool
except ModuleNotFoundError:  # pragma: no cover - fallback when SDK is not installed
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    sdk_src = repo_root / "openai-agents-python" / "src"
    if str(sdk_src) not in sys.path:
        sys.path.append(str(sdk_src))
    from agents import Agent, function_tool  # type: ignore

logging.basicConfig(level=logging.INFO)


class KnowledgeToolResult(BaseModel):
    answer: str = Field(description="Resposta sintetizada usando o contexto recuperado.")
    context: str = Field(description="Trechos dos documentos utilizados para resposta.")
    sources: list[str] = Field(default_factory=list, description="Documentos consultados.")
    confidence: float = Field(
        default=0.0, description="Confiança média estimada a partir da similaridade dos trechos."
    )


current_file = pathlib.Path(__file__).resolve()
project_root = current_file.parents[1]
repo_root = current_file.parents[2]

for path in (project_root, repo_root):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.append(path_str)

try:  # noqa: SIM105
    from AtendentePro import config  # type: ignore[attr-defined]  # noqa: E402
except ImportError:  # pragma: no cover - fallback when executed as script
    import config  # type: ignore  # noqa: E402

if __package__:
    from ..context import ContextNote  # type: ignore
    from .knowledge_prompts import knowledge_prompts_agent  # type: ignore
else:  # pragma: no cover - running as a standalone script
    from context import ContextNote  # type: ignore
    from knowledge_prompts import knowledge_prompts_agent  # type: ignore


@function_tool
async def go_to_rag(question: str) -> KnowledgeToolResult:
    """Utilize o RAG para responder à pergunta do usuário."""
    logging.info("Processing question: %s", question)

    relevant_chunks = __find_relevant_chunks(question, top_k=3)

    if not relevant_chunks:
        return KnowledgeToolResult(
            answer="Não consegui encontrar informações relevantes nos documentos para responder sua pergunta.",
            context="",
            sources=[],
            confidence=0.0,
        )

    context_sections: list[str] = []
    sources: list[str] = []
    seen_sources: set[str] = set()
    similarities: list[float] = []

    for chunk in relevant_chunks:
        chunk_info = chunk.get("chunk", {}) or {}
        source = chunk_info.get("source", "Desconhecido")
        content = chunk_info.get("content", "")
        similarity = float(chunk.get("similarity", 0.0))

        if source not in seen_sources:
            sources.append(source)
            seen_sources.add(source)

        similarities.append(similarity)
        context_sections.append(f"Documento: {source}\nConteúdo: {content}")

    context = "\n\n".join(context_sections)
    logging.info("Context: %s", context)

    confidence = (
        sum(max(score, 0.0) for score in similarities) / len(similarities) if similarities else 0.0
    )

    answer = (
        "Encontrei trechos relevantes, mas não consegui sintetizar uma resposta a partir deles. "
        "Use o contexto abaixo para responder manualmente."
    )

    try:
        from openai import OpenAI

        client = OpenAI(api_key=config.OPENAI_API_KEY)
        completion = client.responses.create(
            model=getattr(config, "DEFAULT_MODEL", "gpt-4.1"),
            input=[
                {
                    "role": "system",
                    "content": (
                        "Você é um especialista em processos fiscais. Use apenas o contexto fornecido para "
                        "responder de forma objetiva. Se não houver informação suficiente, informe isso."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Pergunta: {question}\n\n"
                        f"Contexto:\n{context}\n\n"
                        "Responda em português, destacando os passos principais e cite os documentos utilizados."
                    ),
                },
            ],
        )

        if hasattr(completion, "output_text"):
            answer_candidate = completion.output_text.strip()
            if answer_candidate:
                answer = answer_candidate
        else:
            parts: list[str] = []
            for output in getattr(completion, "output", []):
                for content in getattr(output, "content", []):
                    text_part = getattr(content, "text", None)
                    if text_part:
                        parts.append(text_part)
            if parts:
                answer = "\n".join(parts).strip()
    except Exception as exc:  # noqa: BLE001
        logging.error("Failed to synthesize answer: %s", exc, exc_info=True)

    return KnowledgeToolResult(
        answer=answer,
        context=context,
        sources=sources,
        confidence=confidence,
    )


def __find_relevant_chunks(query: str, top_k: int = 3):
    """Find most relevant chunks for a given query."""
    try:
        from openai import OpenAI
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        client = OpenAI(api_key=config.OPENAI_API_KEY)
        response = client.embeddings.create(model="text-embedding-3-large", input=query)
        query_embedding = response.data[0].embedding

        chunk_embeddings = load_embeddings()
        if not chunk_embeddings:
            logging.error("No embeddings loaded")
            return []

        similarities: list[tuple[float, dict]] = []
        for chunk_data in chunk_embeddings:
            chunk_embedding = chunk_data.get("embedding")
            if not chunk_embedding:
                continue

            query_emb = np.array(query_embedding).reshape(1, -1)
            chunk_emb = np.array(chunk_embedding).reshape(1, -1)
            similarity = cosine_similarity(query_emb, chunk_emb)[0][0]
            similarities.append((similarity, chunk_data))

        similarities.sort(key=lambda x: x[0], reverse=True)

        top_results: list[dict] = []
        for score, chunk_data in similarities[:top_k]:
            enriched_chunk = dict(chunk_data)
            enriched_chunk["similarity"] = score
            top_results.append(enriched_chunk)

        return top_results

    except Exception as exc:  # noqa: BLE001
        logging.error("Error finding relevant chunks: %s", exc, exc_info=True)
        return []


def load_embeddings():
    """Load embeddings from disk."""
    embeddings_path = project_root / "Template" / "knowledge_documentos" / "embedding" / "embeddings.pkl"
    try:
        with open(embeddings_path, "rb") as file:
            loaded_data = pickle.load(file)
            logging.info("Embeddings loaded successfully from %s", embeddings_path)
            return loaded_data
    except Exception as exc:  # noqa: BLE001
        logging.error("Failed to load embeddings from %s: %s", embeddings_path, exc, exc_info=True)
        return []


knowledge_agent = Agent[ContextNote](  # type: ignore[name-defined]
    name="Knowledge Agent",
    handoff_description="Um agente de conhecimento que pode responder a perguntas do usuário.",
    instructions=(
        f"{config.RECOMMENDED_PROMPT_PREFIX} "
        f"{knowledge_prompts_agent}"
    ),
    tools=[go_to_rag],
)
