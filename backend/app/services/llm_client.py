import os
import requests
import json
from typing import Generator, Optional, Dict, Any

class LLMClient:
    """
    Groq API client for Llama-3.3-70B-Versatile with streaming and non-streaming support.
    Handles prompt construction, error handling, retries, and response validation.
    """
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.base_url = base_url or os.getenv("GROQ_API_BASE")
        self.model = "llama-3.3-70b-versatile"
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def build_prompt(self, query: str, context: str, mode: str = "chat") -> str:
        """
        Improved prompt for strict, user-friendly, and citation-aware answers.
        - Only cite page numbers if the answer is directly found in the context.
        - If the answer is not found, reply: 'Not found in document.'
        - Do not hallucinate or add generic citations.
        - Be concise and clear.
        """
        if mode == "deep-dive":
            return (
                "You are an expert assistant. Answer ONLY using the provided document context. "
                "If the answer is not found in the context, reply: 'Not found in document.'\n"
                "Cite page numbers ONLY if the answer is directly found in the context. "
                "Do NOT add citations if the answer is not present.\n"
                "Be concise and clear.\n"
                f"\nContext:\n{context}\n\nQuestion: {query}\nAnswer (with citations):"
            )
        else:
            return (
                "You are a helpful assistant. Answer ONLY using the provided document context. "
                "If the answer is not found in the context, reply: 'Not found in document.'\n"
                "Cite page numbers ONLY if the answer is directly found in the context. "
                "Do NOT add citations if the answer is not present.\n"
                "Be concise and clear.\n"
                f"\nContext:\n{context}\n\nQuestion: {query}\nAnswer:"
            )

    def call_llm(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2, stream: bool = False, retries: int = 3) -> Any:
        """
        Call Groq API for LLM completion. Supports streaming and error retries.
        Returns: generator for streaming, string for non-streaming.
        """
        url = f"{self.base_url}/chat/completions"
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }
        for attempt in range(retries):
            try:
                response = requests.post(url, headers=self.headers, json=payload, stream=stream, timeout=60)
                response.raise_for_status()
                if stream:
                    return self._streaming_response(response)
                else:
                    data = response.json()
                    return self._validate_response(data)
            except Exception as e:
                if attempt == retries - 1:
                    raise RuntimeError(f"LLM API call failed after {retries} attempts: {e}")
        return None

    def _streaming_response(self, response: requests.Response) -> Generator[str, None, None]:
        """Yield tokens from streaming response."""
        for line in response.iter_lines():
            if line:
                try:
                    data = line.decode("utf-8")
                    # Parse and yield only the content part (adjust as per Groq API streaming format)
                    # Groq streaming returns JSON lines
                    chunk = json.loads(data)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
                except Exception:
                    continue

    def _validate_response(self, data: Dict[str, Any]) -> str:
        """Validate and extract answer from LLM response."""
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"].strip()
        raise ValueError("Invalid LLM response format")

    def chat(self, query: str, context: str, mode: str = "chat", **kwargs) -> str:
        prompt = self.build_prompt(query, context, mode)
        return self.call_llm(prompt, stream=False, **kwargs)

    def deep_dive(self, query: str, context: str, **kwargs) -> Generator[str, None, None]:
        prompt = self.build_prompt(query, context, mode="deep-dive")
        return self.call_llm(prompt, stream=True, **kwargs)