from huggingface_hub import InferenceClient
from app.config import settings  

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_client = InferenceClient(
    model=MODEL_NAME,
    token=settings.HUGGINGFACE_API_TOKEN,
)


class EmbeddingError(Exception):
    """Raised when the embedding API call fails."""


def embed_texts(texts:list[str]) -> list[list[float]]:
    if not texts:
        return []
    
    try: 
        result = _client.feature_extraction(texts)
    except Exception as e:
        raise EmbeddingError(f"HuggingFace embedding request failed: {e}") from e
    

    return [list(map(float,vec)) for vec in result]

def embed_text(text: str) -> list[float]:
    """Embed a single string. Convenience wrapper around embed_texts."""
    return embed_texts([text])[0]

