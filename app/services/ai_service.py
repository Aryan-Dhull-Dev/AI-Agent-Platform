# app/services/ai_service.py
from groq import AsyncGroq
from typing import Optional, AsyncGenerator
import os
from datetime import datetime

class AIService:
    def __init__(self):
        """Initialize Groq client with async support"""
        self.client = AsyncGroq(
            api_key=os.getenv("GROQ_API_KEY"),
        )
        self.model = os.getenv("AI_MODEL", "llama-3.1-70b-versatile")
    
    async def chat(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None
    ) -> dict:
        """
        Send chat request to Groq API (sync response)
        
        Args:
            messages: List of message dicts with role/content
            temperature: Sampling temperature (0-1)
            max_tokens: Max tokens to generate
            system_prompt: Optional system prompt for AI behavior
        
        Returns:
            dict with response text and token usage
        """
        # Add system prompt if provided
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
        
        # Call Groq API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Extract response
        response_text = response.choices[0].message.content
        
        # Extract token usage
        token_usage = {
            "tokens_input": response.usage.prompt_tokens,
            "tokens_output": response.usage.completion_tokens,
            "tokens_total": response.usage.total_tokens,
            "cost_usd": 0.0  # Free on Groq! [web:23]
        }
        
        return {
            "response": response_text,
            "token_usage": token_usage,
            "model": self.model,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def stream_chat(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[dict, None]:
        """
        Send chat request with streaming (token-by-token)
        
        Returns:
            Async generator yielding token chunks
        """
        # Add system prompt if provided
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
        
        # Call Groq API with streaming
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        # Yield tokens as they come
        total_tokens_input = 0
        total_tokens_output = 0
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                total_tokens_output += 1
                yield {
                    "token": chunk.choices[0].delta.content,
                    "cumulative_tokens": total_tokens_output
                }
        
        # Final usage data
        yield {
            "done": True,
            "token_usage": {
                "tokens_input": total_tokens_input,
                "tokens_output": total_tokens_output,
                "tokens_total": total_tokens_input + total_tokens_output,
                "cost_usd": 0.0
            }
        }
    
    async def get_model_info(self) -> dict:
        """Get information about current model"""
        return {
            "model": self.model,
            "provider": "Groq",
            "free": True,
            "rate_limit": "30 RPM, 14,400 RPD",
            "speed": "500+ tokens/sec"
        }