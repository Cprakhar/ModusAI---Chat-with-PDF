from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import uuid
import logging
import datetime
from app.services.pdf_processor import PDFTextExtractor
from app.services.vector_store import VectorStore
from app.models.document import DocumentUploadResponse, DocumentListResponse, DocumentDeleteResponse, ErrorResponse, DocumentInfo
from app.utils.deps import get_current_user
from app.models.conversation import ConversationSession

logger = logging.getLogger("chat_with_pdf_api")
document_router = APIRouter()

def get_vector_store():
    return VectorStore()

@document_router.post("/documents/upload", summary="Upload and process a PDF document", response_model=DocumentUploadResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
def upload_document(
    file: UploadFile = File(...),
    vector_store: VectorStore = Depends(get_vector_store),
    user: dict = Depends(get_current_user)
):
    if not file.filename.lower().endswith(('.pdf',)):
        logger.warning(f"Upload rejected: invalid file type {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    # Check file size (max 50MB)
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > 50 * 1024 * 1024:
        logger.warning(f"Upload rejected: file too large {file.filename}")
        raise HTTPException(status_code=400, detail="File too large (max 50MB).")
    try:
        file_id = str(uuid.uuid4())
        file_path = f"/tmp/{file_id}_{file.filename}"
        with open(file_path, "wb") as f_out:
            f_out.write(file.file.read())
        logger.info(f"File saved: {file_path}")
        pdf_processor = PDFTextExtractor(file_path)
        doc_data = pdf_processor.preprocess_document()
        metadata = doc_data["metadata"]
        doc_chunks = doc_data["pages"]
        collection_name = metadata.get("document_id", file_id)
        upload_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        vector_store.save_metadata(collection_name, name=file.filename, upload_time=upload_time)
        vector_store.add_chunks(collection_name, doc_chunks)
        user_id = user["payload"].get("user_id")
        session = ConversationSession(user_id=user_id, document_id=collection_name, user_token=user["token"])
        session.save(user_token=user["token"])
        logger.info(f"Document processed and ingested: {collection_name}, conversation {session.session_id}")
        return {"document_id": collection_name, "conversation_id": session.session_id, "message": "Document uploaded and processed."}
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@document_router.get("/documents", summary="List uploaded documents", response_model=DocumentListResponse)
def list_documents(
    vector_store: VectorStore = Depends(get_vector_store),
    user: dict = Depends(get_current_user)
):
    try:
        docs = vector_store.list_collections()
        logger.info(f"Listed documents: {docs}")
        document_infos = []
        for doc in docs:
            if isinstance(doc, dict) and "document_id" in doc and "name" in doc and "upload_time" in doc:
                document_infos.append(DocumentInfo(**doc))
            else:
                document_infos.append(DocumentInfo(document_id=doc, name=doc, upload_time=""))
        return {"documents": document_infos}
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
