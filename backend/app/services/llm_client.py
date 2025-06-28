import os
import requests
from typing import Generator, Optional, Dict, Any

class LLMClient:
    """
    Groq API client for Llama-3.1-70B-Versatile with streaming and non-streaming support.
    Handles prompt construction, error handling, retries, and response validation.
    """
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.base_url = base_url or "https://api.groq.com/v1"
        self.model = "llama-3.1-70b-versatile"
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def build_prompt(self, query: str, context: str, mode: str = "chat") -> str:
        """Prompt template for chat or deep-dive modes."""
        if mode == "deep-dive":
            return (
                f"You are an expert assistant. Use the provided context to answer the user's question in detail.\n"
                f"Cite page numbers in your answer.\n"
                f"\nContext:\n{context}\n\nQuestion: {query}\nAnswer (with citations):"
            )
        else:
            return (
                f"You are a helpful assistant. Use the context to answer the user's question.\n"
                f"Cite page numbers where relevant.\n"
                f"\nContext:\n{context}\n\nQuestion: {query}\nAnswer:"
            )

    def call_llm(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2, stream: bool = False, retries: int = 3) -> Any:
        """
        Call Groq API for LLM completion. Supports streaming and error retries.
        Returns: generator for streaming, string for non-streaming.
        """
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
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
                    yield data
                except Exception:
                    continue

    def _validate_response(self, data: Dict[str, Any]) -> str:
        """Validate and extract answer from LLM response."""
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"].strip()
        raise ValueError("Invalid LLM response format")

    # Example usage for multi-turn chat
    def chat(self, query: str, context: str, mode: str = "chat", **kwargs) -> str:
        prompt = self.build_prompt(query, context, mode)
        return self.call_llm(prompt, stream=False, **kwargs)

    # Example usage for deep-dive with streaming
    def deep_dive(self, query: str, context: str, **kwargs) -> Generator[str, None, None]:
        prompt = self.build_prompt(query, context, mode="deep-dive")
        return self.call_llm(prompt, stream=True, **kwargs)
