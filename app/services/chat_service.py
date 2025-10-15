from openai import OpenAI
from app.config import settings
from app.services.retrieval_service import RetrievalService
from typing import List, Dict, Optional
import uuid

class ChatService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.retrieval_service = RetrievalService()
        self.conversations = {}  # In-memory (use DB in production)
    
    def chat(self, message: str, workspace_id: str, 
             conversation_id: Optional[str] = None,
             filters: Optional[Dict] = None,
             prompt_template: Optional[str] = None) -> Dict:
        """Chat with RAG"""
        
        # Create or get conversation
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            self.conversations[conversation_id] = []
        
        # Retrieve relevant context
        search_results = self.retrieval_service.hybrid_search(
            query=message,
            workspace_id=workspace_id,
            filters=filters
        )
        
        # Build context
        context = self._build_context(search_results)
        
        # Build prompt
        system_prompt = prompt_template or self._default_system_prompt()
        user_prompt = self._build_user_prompt(message, context)
        
        # Get conversation history
        history = self.conversations.get(conversation_id, [])
        
        # Build messages for OpenAI
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add history (last 5 exchanges)
        for msg in history[-10:]:
            messages.append(msg)
        
        # Add current query
        messages.append({"role": "user", "content": user_prompt})
        
        # Call LLM
        response = self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            temperature=settings.LLM_TEMPERATURE
        )
        
        assistant_message = response.choices[0].message.content
        
        # Update conversation history
        self.conversations[conversation_id].append(
            {"role": "user", "content": message}
        )
        self.conversations[conversation_id].append(
            {"role": "assistant", "content": assistant_message}
        )
        
        return {
            "response": assistant_message,
            "sources": search_results,
            "conversation_id": conversation_id
        }
    
    def _build_context(self, search_results: List[Dict]) -> str:
        """Format search results into context"""
        
        if not search_results:
            return "No relevant information found."
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            context_parts.append(
                f"[Source {i}]\n{result['content']}\n"
            )
        
        return "\n".join(context_parts)
    
    def _default_system_prompt(self) -> str:
        """Default system prompt"""
        return """You are a helpful AI assistant. You answer questions based on the provided context.

Rules:
1. Only use information from the provided context
2. If the context doesn't contain relevant information, say so
3. Cite sources when appropriate [Source N]
4. Be concise and accurate
5. If asked about something not in the context, politely explain you can only answer based on the available documents"""
    
    def _build_user_prompt(self, query: str, context: str) -> str:
        """Build user prompt with context"""
        return f"""Context:
{context}

Question: {query}

Please answer based on the context provided above."""