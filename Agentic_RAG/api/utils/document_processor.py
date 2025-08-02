import fitz  # PyMuPDF
import tempfile
import os
from fastapi import UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract plain text from PDF - simple and efficient for RAG"""
    doc = fitz.open(pdf_path)
    try:
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        return text.strip()
    finally:
        doc.close()

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
    """Split text into overlapping chunks using LangChain's intelligent splitter"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )
    return text_splitter.split_text(text)

async def process_upload_file(file: UploadFile) -> dict:
    """Convert UploadFile to text chunks for RAG processing"""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(temp_path)
        
        # Split into chunks
        chunks = chunk_text(text)
        
        return {
            "filename": file.filename,
            "total_text_length": len(text),
            "chunks_count": len(chunks),
            "chunks": chunks
        }
    finally:
        # Cleanup
        os.unlink(temp_path)
