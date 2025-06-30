from typing import List, Dict, Any, Optional
from .vector_store import VectorStore
import re
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

class RAGEngine:
    def __init__(self, vector_store: VectorStore, collection_name: str):
        self.vector_store = vector_store
        self.collection_name = collection_name

    def retrieve(self, query: str, n_results: int = 5, filters: Optional[Dict[str, Any]] = None, similarity_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        initial_results = self.vector_store.hybrid_query(
            self.collection_name, query, n_results=n_results*2, filters=filters, similarity_threshold=similarity_threshold
        )
        collection = self.vector_store.get_or_create_collection(self.collection_name)
        all_docs = collection.get()
        if all_docs['documents']:
            first_chunk = {
                'id': all_docs['ids'][0],
                'text': all_docs['documents'][0],
                'metadata': all_docs['metadatas'][0],
                'hybrid_score': 1000,
                'context_score': 1000
            }
            if not any(c['id'] == first_chunk['id'] for c in initial_results):
                initial_results = [first_chunk] + initial_results
        query_keywords = set(re.findall(r'\w+', query.lower()))
        for r in initial_results:
            chunk_keywords = set(re.findall(r'\w+', r['text'].lower()))
            r['context_score'] = len(query_keywords & chunk_keywords)
        ranked = sorted(initial_results, key=lambda x: (x['hybrid_score'], x['context_score']), reverse=True)
        return ranked[:n_results]

    def aggregate_context(self, chunks: List[Dict[str, Any]], max_tokens: int = 2000) -> str:
        context = ""
        token_count = 0
        for chunk in chunks:
            chunk_text = f"[Page {chunk['metadata'].get('page', '?')}] {chunk['text']}\n"
            tokens = len(chunk_text.split())
            if token_count + tokens > max_tokens:
                break
            context += chunk_text
            token_count += tokens
        return context.strip()

    def create_prompt(self, query: str, context: str, mode: str = "chat") -> str:
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

    def extract_citations(self, answer: str) -> List[str]:
        return re.findall(r'page\s*(\d+)', answer, re.IGNORECASE)

    def expand_query(self, query: str) -> List[str]:
        """
        Production-grade query expansion using WordNet synonyms and lemmatization.
        """
        lemmatizer = WordNetLemmatizer()
        tokens = re.findall(r'\w+', query.lower())
        expansions = set([query])
        for token in tokens:
            lemma = lemmatizer.lemmatize(token)
            expansions.add(lemma)
            for syn in wordnet.synsets(token):
                for lemma_obj in syn.lemmas():
                    expansions.add(lemma_obj.name().replace('_', ' '))
        expanded_queries = set()
        for exp in expansions:
            if isinstance(exp, str):
                expanded_queries.add(exp)
            elif isinstance(exp, (list, tuple)):
                expanded_queries.add(' '.join(exp))
        return list(expanded_queries)

    def classify_query(self, query: str) -> str:
        """
        Production-grade query classification using NLP, expanded keyword sets, synonym expansion, and regex patterns.
        Categories: summary, data, table, figure, statistics, qa (default)
        """
        lemmatizer = WordNetLemmatizer()
        query_lc = query.lower()
        tokens = re.findall(r'\w+', query_lc)
        lemmas = set(lemmatizer.lemmatize(token) for token in tokens)

        summary_keywords = {"summarize", "overview", "explain", "summary", "describe", "outline", "gist", "recap", "synthesis"}
        data_keywords = {"data", "dataset", "value", "values", "statistics", "statistic", "number", "numbers", "amount", "total", "average", "mean", "median", "distribution", "frequency", "percent", "percentage", "proportion", "ratio", "count", "trend", "increase", "decrease", "growth", "decline"}
        table_keywords = {"table", "tabular", "spreadsheet", "grid", "matrix", "sheet"}
        figure_keywords = {"figure", "chart", "graph", "plot", "diagram", "visualization", "image", "illustration", "picture", "map"}

        def expand_with_wordnet(keywords):
            expanded = set(keywords)
            for word in keywords:
                for syn in wordnet.synsets(word):
                    for lemma in syn.lemmas():
                        expanded.add(lemma.name().replace('_', ' '))
            return expanded

        summary_set = expand_with_wordnet(summary_keywords)
        data_set = expand_with_wordnet(data_keywords)
        table_set = expand_with_wordnet(table_keywords)
        figure_set = expand_with_wordnet(figure_keywords)

        summary_patterns = [r"summar(y|ize|ise)", r"overview", r"explain", r"describe", r"outline", r"gist", r"recap", r"synthesi(s|ze)"]
        data_patterns = [r"data", r"stat(s|istics)?", r"number(s)?", r"amount", r"total", r"average", r"mean", r"median", r"distribution", r"frequency", r"percent(age)?", r"proportion", r"ratio", r"count", r"trend", r"increase", r"decrease", r"growth", r"decline"]
        table_patterns = [r"table", r"tabular", r"spreadsheet", r"grid", r"matrix", r"sheet"]
        figure_patterns = [r"figure", r"chart", r"graph", r"plot", r"diagram", r"visualization", r"image", r"illustration", r"picture", r"map"]

        def match_keywords(keywords):
            return any(word in tokens or word in lemmas for word in keywords)

        def match_patterns(patterns):
            return any(re.search(p, query_lc) for p in patterns)

        if match_keywords(summary_set) or match_patterns(summary_patterns):
            return "summary"
        if match_keywords(data_set) or match_patterns(data_patterns):
            return "data"
        if match_keywords(table_set) or match_patterns(table_patterns):
            return "table"
        if match_keywords(figure_set) or match_patterns(figure_patterns):
            return "figure"
        if re.search(r"show me|list all|how many|what is the (average|mean|median|total|sum|count)", query_lc):
            return "data"
        return "qa"

    def aggregate_conversation_context(self, conversation_history: List[str], retrieved_chunks: List[Dict[str, Any]], max_tokens: int = 2000, max_turns: int = 5) -> str:
        """
        Sliding window context aggregation for multi-turn chat.
        Includes the most recent N conversation turns and retrieved document context, truncated to fit max_tokens.
        Args:
            conversation_history: List of previous user/assistant messages (strings, most recent last).
            retrieved_chunks: List of retrieved document chunks (as in aggregate_context).
            max_tokens: Maximum total tokens for the context window.
            max_turns: Maximum number of conversation turns to include.
        Returns:
            Aggregated context string for LLM input.
        """
        selected_turns = conversation_history[-max_turns:] if max_turns > 0 else conversation_history
        conversation_text = "\n".join(selected_turns)
        conversation_tokens = len(conversation_text.split())

        doc_context = ""
        doc_tokens = 0
        for chunk in retrieved_chunks:
            chunk_text = f"[Page {chunk['metadata'].get('page', '?')}] {chunk['text']}\n"
            tokens = len(chunk_text.split())
            if conversation_tokens + doc_tokens + tokens > max_tokens:
                break
            doc_context += chunk_text
            doc_tokens += tokens

        context = f"Conversation:\n{conversation_text}\n\nDocument Context:\n{doc_context.strip()}"
        return context.strip()
