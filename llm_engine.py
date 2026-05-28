import os
from abc import ABC, abstractmethod
import anthropic
from dotenv import load_dotenv

load_dotenv()

class LLMProvider(ABC):
    @abstractmethod
    def get_response(self, messages, system_prompt):
        pass

class ClaudeProvider(LLMProvider):
    def __init__(self, api_key=None, model=None):
        self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-opus-4-7")

    def get_response(self, messages, system_prompt):
        try:
            # Convert messages to Anthropic format if necessary
            # Anthropic expects messages to start with user and alternate
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=messages
            )
            return response.content[0].text
        except Exception as e:
            return f"Error with Claude: {str(e)}"

# Factory function to get the requested provider
def get_llm_provider(provider_type="claude"):
    if provider_type == "claude":
        return ClaudeProvider()
    # Add Gemini here in the future
    # elif provider_type == "gemini":
    #     return GeminiProvider()
    else:
        raise ValueError(f"Unsupported provider: {provider_type}")

# Standard Tutor Persona
TUTOR_SYSTEM_PROMPT = """
You are a friendly and encouraging English Tutor. Your goal is to help the user practice speaking and listening.
Based on the provided content (blog or video transcript) or a specific topic, you must:
1. MANDATORY: End every single response with exactly one clear, engaging question to keep the user talking.
2. If the user makes a clear grammatical mistake, gently provide a correction after answering their point.
3. Keep your responses concise (2-3 sentences max) so the user can listen and respond easily.
4. Encourage the user to speak more and explain their thoughts.
5. Do not just say "hello" or "I'm ready". Start the conversation by discussing the content and asking a question.
"""
