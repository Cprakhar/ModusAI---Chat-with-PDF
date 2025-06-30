import fitz
import pdfplumber
import uuid
from typing import List, Dict, Any

class PDFTextExtractor:
    """
    Extracts text and basic structure from PDF using PyMuPDF.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.doc = fitz.open(file_path)

    def extract_text_by_page(self) -> List[Dict[str, Any]]:
        """
        Extracts text from each page, preserving page numbers.
        Returns a list of dicts: [{"page": int, "text": str}]
        """
        pages = []
        for page_num in range(len(self.doc)):
            page = self.doc.load_page(page_num)
            text = page.get_text("text")
            pages.append({
                "page": page_num + 1,
                "text": text
            })
        return pages

    def extract_structured_text_by_page(self) -> List[Dict[str, Any]]:
        """
        Extracts structured text (blocks, headers, paragraphs, lists) from each page using PyMuPDF.
        Returns a list of dicts: [{"page": int, "blocks": List[Dict]}]
        """
        pages = []
        for page_num in range(len(self.doc)):
            page = self.doc.load_page(page_num)
            blocks = page.get_text("dict").get("blocks", [])
            structured_blocks = []
            for block in blocks:
                if block["type"] == 0:
                    text = block.get("lines", [])
                    block_text = " ".join([span["text"] for line in text for span in line.get("spans", [])])
                    structured_blocks.append({
                        "bbox": block.get("bbox"),
                        "text": block_text,
                        "type": "text"
                    })
                elif block["type"] == 1:
                    structured_blocks.append({
                        "bbox": block.get("bbox"),
                        "type": "image"
                    })
            pages.append({
                "page": page_num + 1,
                "blocks": structured_blocks
            })
        return pages

    def extract_tables_by_page(self) -> List[Dict[str, Any]]:
        """
        Extracts tables from each page using pdfplumber.
        Returns a list of dicts: [{"page": int, "tables": List[List[List[str]]]}]
        """
        tables = []
        with pdfplumber.open(self.file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_tables = page.extract_tables()
                tables.append({
                    "page": page_num + 1,
                    "tables": page_tables
                })
        return tables

    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extracts PDF metadata (title, author, etc.) and page count.
        """
        metadata = self.doc.metadata or {}
        metadata['page_count'] = len(self.doc)
        return metadata

    def extract_images_by_page(self) -> List[Dict[str, Any]]:
        """
        Extracts images from each page using PyMuPDF.
        Returns a list of dicts: [{"page": int, "images": List[Dict]}]
        Each image dict contains: {"xref": int, "ext": str, "bytes": bytes}
        """
        images = []
        for page_num in range(len(self.doc)):
            page = self.doc.load_page(page_num)
            page_images = []
            for img in page.get_images(full=True):
                xref = img[0]
                base_image = self.doc.extract_image(xref)
                image_bytes = base_image.get("image")
                ext = base_image.get("ext")
                page_images.append({
                    "xref": xref,
                    "ext": ext,
                    "bytes": image_bytes
                })
            images.append({
                "page": page_num + 1,
                "images": page_images
            })
        return images

    def preprocess_document(self) -> Dict[str, Any]:
        """
        Combines structured text, tables, images, and metadata for each page into a unified structure.
        Handles various encodings and maintains page number mapping.
        Returns a dict with metadata and a list of pages.
        """
        structured_text_pages = self.extract_structured_text_by_page()
        table_pages = self.extract_tables_by_page()
        image_pages = self.extract_images_by_page()
        metadata = self.extract_metadata()
        page_count = metadata.get('page_count', len(structured_text_pages))
        document = []
        for i in range(page_count):
            block_texts = [block["text"] for block in structured_text_pages[i]["blocks"] if "text" in block]
            page_text = " ".join(block_texts)
            chunk_id = f"{metadata.get('document_id', str(uuid.uuid4()))}_page_{i+1}"
            doc_id = metadata.get("document_id") or self.file_path.split("/")[-1].split(".")[0]
            page_data = {
                "chunk_id": chunk_id,
                "page": i + 1,
                "text": page_text,
                "blocks": structured_text_pages[i]["blocks"] if i < len(structured_text_pages) else [],
                "tables": table_pages[i]["tables"] if i < len(table_pages) else [],
                "images": image_pages[i]["images"] if i < len(image_pages) else [],
                "metadata": {**{k: v for k, v in metadata.items() if v is not None}, "document_id": doc_id}
            }
            document.append(page_data)
        return {
            "metadata": metadata,
            "pages": document
        }

    def close(self):
        self.doc.close()
