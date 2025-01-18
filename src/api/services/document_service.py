import asyncio
from typing import List
import logging
from pathlib import Path
import aiofiles
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
import chromadb

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        self.vector_store = None
        self.embeddings = OllamaEmbeddings(
            base_url="http://ollama:11434",
            model="llama2"
        )
        self.text_splitter = CharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.persist_directory = "/app/data/vectorstore"

    async def initialize(self):
        """Initialize the vector store"""
        try:
            Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
            
            client = chromadb.PersistentClient(path=self.persist_directory)
            self.vector_store = Chroma(
                client=client,
                embedding_function=self.embeddings,
                collection_name="document_store"
            )
            logger.info("Vector store initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise

    async def process_document(self, file) -> str:
        try:
            if not self.vector_store:
                await self.initialize()

            # Save uploaded file
            file_path = Path(f"/app/data/uploads/{file.filename}")
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)

            # Load and split document
            loader = TextLoader(str(file_path))
            documents = loader.load()
            texts = self.text_splitter.split_documents(documents)

            # Add to vector store
            if texts:
                await asyncio.to_thread(
                    self.vector_store.add_documents,
                    texts
                )
                logger.info(f"Document processed and added to vector store: {file.filename}")
            else:
                logger.warning("No texts extracted from document")

            return str(file_path)

        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise

    async def get_retriever(self):
        """Get the vector store retriever"""
        if not self.vector_store:
            await self.initialize()
        return self.vector_store.as_retriever()

    async def cleanup(self):
        """Cleanup resources"""
        if self.vector_store:
            self.vector_store.persist() 