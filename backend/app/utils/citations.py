from typing import Dict, Any, List, Optional

class Citation:
    def __init__(self, document_id: str, page: int, chunk_id: Optional[str] = None, snippet: Optional[str] = None, confidence: Optional[float] = None, citation_type: str = "text"):
        self.document_id = document_id
        self.page = page
        self.chunk_id = chunk_id
        self.snippet = snippet
        self.confidence = confidence
        self.citation_type = citation_type  # e.g., 'text', 'table', 'figure'

    def format(self) -> str:
        doc_part = f"Document: {self.document_id}" if self.document_id else "Document: unknown"
        page_part = f"Page: {self.page}" if self.page else "Page: ?"
        chunk_part = f"Chunk: {self.chunk_id}" if self.chunk_id else ""
        type_part = f"Type: {self.citation_type}" if self.citation_type else ""
        # Compose formatted string
        formatted = f"[{doc_part} | {page_part}"
        if chunk_part:
            formatted += f" | {chunk_part}"
        if type_part:
            formatted += f" | {type_part}"
        formatted += "]"
        return formatted

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "page": self.page,
            "chunk_id": self.chunk_id,
            "snippet": self.snippet,
            "confidence": self.confidence,
            "citation_type": self.citation_type,
            "formatted": self.format()
        }

def extract_citations_from_chunks(chunks: List[Dict[str, Any]], answer: str) -> List[Citation]:
    """
    Extract citations from answer and match to chunks by page number.
    Returns a list of Citation objects.
    """
    import re
    citations = []
    page_numbers = set(int(p) for p in re.findall(r'page\s*(\d+)', answer, re.IGNORECASE))
    for chunk in chunks:
        page = chunk["metadata"].get("page")
        if page in page_numbers:
            citations.append(Citation(
                document_id=chunk["metadata"].get("document_id", "unknown"),
                page=page,
                chunk_id=chunk.get("id"),
                snippet=chunk["text"][:200],  # First 200 chars as snippet
                confidence=chunk.get("hybrid_score"),
                citation_type=chunk["metadata"].get("type", "text")
            ))
    return citations

def validate_citation(citation: Citation, document_pages: List[int], chunk_ids: Optional[List[str]] = None) -> bool:
    """
    Validate that the citation refers to an existing page and (optionally) chunk.
    """
    if citation.page not in document_pages:
        return False
    if chunk_ids and citation.chunk_id and citation.chunk_id not in chunk_ids:
        return False
    return True
