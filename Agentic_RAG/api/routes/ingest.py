# Document Ingestion Endpoint

from api.utils.document_processor import process_upload_file
from fastapi import APIRouter, UploadFile, File


router = APIRouter()

@router.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    try:
        result = await process_upload_file(file)
        return result
    except Exception as e:
        return {"error": f"Processing failed: {str(e)}"}







