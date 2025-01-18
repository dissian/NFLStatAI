from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
import logging
from ..models.chat import ChatRequest, ChatResponse
from ..services.chat_service import ChatService
from ..services.document_service import DocumentService

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)

chat_service = ChatService()
document_service = DocumentService()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        result = await document_service.process_document(file)
        return {"message": "Document processed successfully", "document_id": result}
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    try:
        response = await chat_service.process_query(request.query)
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 