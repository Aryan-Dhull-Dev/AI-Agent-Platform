# app/services/prompt_manager.py
from typing import Optional

class PromptManager:
    """Centralized prompt templates for different modes"""
    
    # Default system prompt
    DEFAULT_SYSTEM_PROMPT = """You are a helpful AI assistant powered by Llama 3.1 70B via Groq. 
You provide accurate, concise, and helpful responses. 
If the user asks for code, provide production-ready examples with explanations."""
    
    # Code generation mode
    CODE_GENERATION_PROMPT = """You are a senior Python engineer specializing in FastAPI, PostgreSQL, and cloud infrastructure.
Your task is to generate production-ready code with:
- Proper error handling
- Type hints
- Docstrings
- Security considerations (authentication, input validation)
- Async/await patterns where appropriate

When generating code:
1. Explain what the code does
2. Provide the complete code
3. Suggest how to test it"""
    
    # Architecture mode
    ARCHITECTURE_PROMPT = """You are a cloud architect specializing in GCP, Kubernetes, and scalable systems.
Your task is to design efficient, scalable architectures.

When providing architecture:
1. Explain the components and their roles
2. Discuss trade-offs and alternatives
3. Include diagrams (Mermaid format if possible)
4. Consider cost, performance, and reliability"""
    
    # Debugging mode
    DEBUGGING_PROMPT = """You are a debugging expert who helps diagnose and fix issues.

When debugging:
1. Analyze the error message
2. Identify the root cause
3. Provide a step-by-step fix
4. Suggest how to prevent similar issues"""
    
    @staticmethod
    def get_prompt(mode: Optional[str] = None) -> str:
        """Get prompt based on mode"""
        prompts = {
            "code": PromptManager.CODE_GENERATION_PROMPT,
            "architecture": PromptManager.ARCHITECTURE_PROMPT,
            "debugging": PromptManager.DEBUGGING_PROMPT,
            "default": PromptManager.DEFAULT_SYSTEM_PROMPT
        }
        return prompts.get(mode, prompts["default"])
    
    @staticmethod
    def create_conversation_messages(
        user_message: str,
        history: list = [],
        mode: Optional[str] = None
    ) -> list:
        """
        Create messages array for Groq API with conversation history
        
        Args:
            user_message: Current user input
            history: List of previous messages (role, content)
            mode: Prompt mode (code, architecture, debugging, default)
        
        Returns:
            Messages array for API call
        """
        messages = []
        
        # Add system prompt
        system_prompt = PromptManager.get_prompt(mode)
        messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history (last 10 messages)
        for msg in history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages