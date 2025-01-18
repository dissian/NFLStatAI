import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from langchain_community.llms import Ollama
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from .document_service import DocumentService

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.llm = Ollama(
            base_url="http://ollama:11434",
            model="llama2"
        )
        self.document_service = DocumentService()
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_template("""Answer the following question based on the provided context:

        Context: {context}
        Question: {question}

        Answer the question in a helpful and detailed way.""")
        
        # Create the document chain
        self.document_chain = create_stuff_documents_chain(
            llm=self.llm,
            prompt=prompt
        )

    async def process_query(self, query: str) -> str:
        try:
            # Get document embeddings and create retrieval chain
            retriever = await self.document_service.get_retriever()
            retrieval_chain = create_retrieval_chain(
                self.document_chain,
                retriever
            )
            
            # Process query in thread pool
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                self.executor,
                lambda: retrieval_chain.invoke({
                    "input": query
                })
            )

            # Update conversation memory
            self.memory.save_context(
                {"input": query},
                {"output": response["answer"]}
            )

            return response["answer"]

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise 