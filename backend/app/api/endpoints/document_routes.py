from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import uuid
import logging
from app.services.pdf_processor import PDFTextExtractor
from app.services.vector_store import VectorStore
from app.models import DocumentUploadResponse, DocumentListResponse, DocumentDeleteResponse, ErrorResponse

logger = logging.getLogger("chat_with_pdf_api")
document_router = APIRouter()

def get_pdf_processor():
    return PDFTextExtractor()

def get_vector_store():
    return VectorStore()

@document_router.post("/documents/upload", summary="Upload and process a PDF document", response_model=DocumentUploadResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
def upload_document(
    file: UploadFile = File(...),
    pdf_processor: PDFTextExtractor = Depends(get_pdf_processor),
    vector_store: VectorStore = Depends(get_vector_store)
):
    if not file.filename.lower().endswith(('.pdf',)):
        logger.warning(f"Upload rejected: invalid file type {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    if file.spool_max_size and file.spool_max_size > 50 * 1024 * 1024:
        logger.warning(f"Upload rejected: file too large {file.filename}")
        raise HTTPException(status_code=400, detail="File too large (max 50MB).")
    try:
        file_id = str(uuid.uuid4())
        file_path = f"/tmp/{file_id}_{file.filename}"
        with open(file_path, "wb") as f_out:
            f_out.write(file.file.read())
        logger.info(f"File saved: {file_path}")
        doc_chunks, metadata = pdf_processor.preprocess_document(file_path)
        collection_name = metadata["document_id"]
        vector_store.add_documents(collection_name, doc_chunks)
        logger.info(f"Document processed and ingested: {collection_name}")
        return {"document_id": collection_name, "message": "Document uploaded and processed."}
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@document_router.get("/documents", summary="List uploaded documents", response_model=DocumentListResponse)
def list_documents(vector_store: VectorStore = Depends(get_vector_store)):
    try:
        docs = vector_store.list_collections()
        logger.info(f"Listed documents: {docs}")
        return {"documents": docs}
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@document_router.delete("/documents/{document_id}", summary="Remove a document", response_model=DocumentDeleteResponse)
def delete_document(document_id: str, vector_store: VectorStore = Depends(get_vector_store)):
    try:
        vector_store.delete_collection(document_id)
        logger.info(f"Deleted document: {document_id}")
        return {"message": f"Document {document_id} deleted."}
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
