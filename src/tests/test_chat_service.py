import pytest
import asyncio
from ..api.services.chat_service import ChatService
from ..api.services.document_service import DocumentService

@pytest.mark.asyncio
async def test_chat_service():
    chat_service = ChatService()
    
    # Test query processing
    response = await chat_service.process_query("What is the capital of France?")
    assert isinstance(response, str)
    assert len(response) > 0

@pytest.mark.asyncio
async def test_document_service():
    document_service = DocumentService()
    
    # Test initialization
    await document_service.initialize()
    assert document_service.vector_store is not None
    
    # Test retriever
    retriever = await document_service.get_retriever()
    assert retriever is not None 