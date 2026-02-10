"""
Query workflow nodes.

Each node performs a specific step in the RAG query pipeline:
1. embed_query_node: Generate query embedding
2. retrieve_chunks_node: Retrieve relevant chunks from vector store
3. format_context_node: Format chunks into context string
4. generate_answer_node: Generate answer using LLM
"""

import os
import time
from typing import Any, Dict

from openai import AsyncOpenAI

from app.core.errors import DocumentProcessingError, EmbeddingError
from app.core.logging import get_logger
from app.rag.embeddings.base import BaseEmbedder
from app.rag.graphs.query_state import QueryState
from app.rag.storage.base import BaseVectorStore
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver  
memory = InMemorySaver()

llm = ChatOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4o-mini",
    temperature=0
)
system_prompt = """
You are a helpful assistant.

Rules:
- Answer based on provided context if available
- If no context, answer from your knowledge
- Be concise
"""
agent = create_agent(
    model=llm,
    system_prompt=system_prompt,
    checkpointer=memory,
)
logger = get_logger(__name__)

async def embed_query_node(state: QueryState, embedder: BaseEmbedder) -> Dict[str, Any]:
    """
    Generate embedding for the user query.

    Args:
        state (QueryState): Current query state.
        embedder (BaseEmbedder): Embedding provider instance.

    Returns:
        Dict[str, Any]: Updated state with query_embedding and status.
    """
    try:
        logger.info(f"Generating embedding for query: {state['query'][:100]}")

        # Generate embedding for query
        query_embedding = await embedder.embed_query(state["query"])

        logger.info(f"Query embedding generated: {len(query_embedding)} dimensions")

        return {
            "query_embedding": query_embedding,
            "status": "embedding_complete",
        }

    except Exception as e:
        logger.error(f"Error generating query embedding: {e}")
        return {
            "errors": state.get("errors", []) + [f"Embedding error: {str(e)}"],
            "status": "failed",
        }


async def retrieve_chunks_node(state: QueryState, vector_store: BaseVectorStore) -> Dict[str, Any]:
    """
    Retrieve relevant chunks from vector store.

    Args:
        state (QueryState): Current query state.
        vector_store (BaseVectorStore): Vector store instance.

    Returns:
        Dict[str, Any]: Updated state with retrieved_chunks and status.
    """
    try:
        query_embedding = state.get("query_embedding")
        if not query_embedding:
            raise DocumentProcessingError("Query embedding not found in state")

        logger.info(f"Retrieving top {state['top_k']} chunks from vector store")

        # Perform similarity search
        retrieved_chunks = await vector_store.similarity_search(
            query_embedding=query_embedding,
            k=state["top_k"],
            filter_metadata=state.get("filter_metadata"),
        )

        logger.info(f"Retrieved {len(retrieved_chunks)} chunks")

        return {
            "retrieved_chunks": retrieved_chunks,
            "status": "retrieval_complete",
        }

    except Exception as e:
        logger.error(f"Error retrieving chunks: {e}")
        return {
            "errors": state.get("errors", []) + [f"Retrieval error: {str(e)}"],
            "status": "failed",
        }


async def format_context_node(state: QueryState, max_length: int) -> Dict[str, Any]:
    """
    Format retrieved chunks into context string.

    Args:
        state (QueryState): Current query state.
        max_length (int): Maximum context length in characters.

    Returns:
        Dict[str, Any]: Updated state with formatted context and status.
    """
    try:
        retrieved_chunks = state.get("retrieved_chunks", [])

        if not retrieved_chunks:
            logger.warning("No chunks retrieved, returning empty context")
            return {
                "context": "",
                "status": "formatting_complete",
            }

        logger.info(f"Formatting {len(retrieved_chunks)} chunks into context")

        # Build context with source attribution
        context_parts = []
        current_length = 0

        for i, chunk in enumerate(retrieved_chunks, 1):
            # Format chunk with source information
            chunk_text = f"[Document {i}: {chunk.metadata.filename}]\n{chunk.content}\n---\n"

            # Check if adding this chunk would exceed max length
            if current_length + len(chunk_text) > max_length:
                logger.info(f"Context length limit reached, including {i-1}/{len(retrieved_chunks)} chunks")
                break

            context_parts.append(chunk_text)
            current_length += len(chunk_text)

        context = "\n".join(context_parts)

        logger.info(f"Context formatted: {len(context)} characters")

        return {
            "context": context,
            "status": "formatting_complete",
        }

    except Exception as e:
        logger.error(f"Error formatting context: {e}")
        return {
            "errors": state.get("errors", []) + [f"Formatting error: {str(e)}"],
            "status": "failed",
        }


async def generate_answer_node(
    state: QueryState,
    llm_client: AsyncOpenAI,
    model: str,
    temperature: float,
) -> Dict[str, Any]:
    """
    Generate answer using LLM based on context.

    Args:
        state (QueryState): Current query state.
        llm_client (AsyncOpenAI): OpenAI client instance.
        model (str): LLM model name.
        temperature (float): Temperature for generation.

    Returns:
        Dict[str, Any]: Updated state with answer, query_end_time, and status.
    """
    try:
        context = state.get("context", "")
        query = state["query"]

        # logger.info(f"Context are:{context}, Query is:{query}")

        # logger.info(f"Generating answer using model: {model}")

        # Lazy import to avoid circular dependency
        # Reason: QueryAgent depends on modules that eventually import query_nodes
        from pydantic_ai import Agent

        # Build system prompt for grounded RAG
        system_prompt = """You are a helpful assistant that answers questions  on the provided context if relevant context not found give answer in your knowledgebase.

RULES:
1. Be concise and precise in your answers"""

        # Build user prompt
        if context:
            user_prompt = f"""Context from documents:

{context}

Question: {query}
"""
        else:
            user_prompt = f"""Question: {query}

"""

      
        messages = []
        if context:
                  messages.append({
                   "role": "system",
                    "content": f"Context from documents:\n{context}"
                  })
                 
  
        messages.append({
                  "role": "user",
                  "content": query
                  })       
        result = agent.invoke(
           {"messages": [{"role": "user", "content": user_prompt}]},
           {"configurable": {"thread_id": "1"}},  
        )
        ai_message = result["messages"][-1].content
        answer = ai_message or "No answer generated."
        # print(f"messages_history: {history}")
        # logger.info(f"Answer generated: {len(answer)} characters")

        return {
            "answer": answer,
            "query_end_time": time.time(),
            "status": "completed",
        }

    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        return {
            "answer": "Error generating answer. Please try again.",
            "errors": state.get("errors", []) + [f"Generation error: {str(e)}"],
            "query_end_time": time.time(),
            "status": "failed",
        }
