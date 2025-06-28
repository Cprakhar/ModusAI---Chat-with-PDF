from typing import List, Dict, Any
import re

class Chunker:
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_text_semantic(self, text: str) -> List[str]:
        """
        Splits text into paragraphs/sections using semantic boundaries (e.g., double newlines, headers).
        """
        # Split on double newlines or section headers
        sections = re.split(r'(?:\n\s*\n|\n\s*#)', text)
        return [s.strip() for s in sections if s.strip()]

    def chunk_with_overlap(self, sections: List[str]) -> List[str]:
        """
        Chunks sections into fixed-size windows with overlap, preserving boundaries where possible.
        """
        chunks = []
        current_chunk = []
        current_length = 0
        for section in sections:
            section_length = len(section)
            if current_length + section_length > self.chunk_size:
                # Finalize current chunk
                chunk_text = '\n'.join(current_chunk)
                chunks.append(chunk_text)
                # Start new chunk with overlap
                overlap_text = chunk_text[-self.overlap:] if self.overlap > 0 else ''
                current_chunk = [overlap_text, section] if overlap_text else [section]
                current_length = len('\n'.join(current_chunk))
            else:
                current_chunk.append(section)
                current_length += section_length
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        return [c for c in chunks if c.strip()]

    def chunk_page(self, page: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunks a single page's text and attaches metadata (page number, tables, images).
        Returns a list of chunk dicts.
        """
        text = '\n'.join([block['text'] for block in page.get('blocks', []) if block.get('type') == 'text'])
        sections = self.split_text_semantic(text)
        text_chunks = self.chunk_with_overlap(sections)
        chunks = []
        for idx, chunk_text in enumerate(text_chunks):
            chunk = {
                'chunk_id': f"{page['page']}_{idx+1}",
                'page': page['page'],
                'text': chunk_text,
                'tables': page.get('tables', []),
                'images': page.get('images', []),
                'metadata': {
                    'chunk_index': idx,
                    'page': page['page']
                }
            }
            chunks.append(chunk)
        return chunks

    def chunk_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunks the entire document (output of PDFTextExtractor.preprocess_document).
        Returns a list of metadata-rich chunk dicts.
        """
        all_chunks = []
        for page in document.get('pages', []):
            page_chunks = self.chunk_page(page)
            all_chunks.extend(page_chunks)
        return all_chunks
