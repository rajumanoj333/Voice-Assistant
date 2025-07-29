from openai import OpenAI
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import json

load_dotenv()

class LLMProcessor:
    def __init__(self):
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=api_key)
        
        # Default model configuration
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.max_tokens = int(os.getenv('MAX_TOKENS', '150'))
        self.temperature = float(os.getenv('TEMPERATURE', '0.7'))
        
        # System prompt for the voice assistant
        self.system_prompt = """
        You are a helpful voice assistant. You should:
        1. Provide concise, clear responses suitable for speech
        2. Be conversational and natural
        3. Keep responses under 2-3 sentences when possible
        4. Ask clarifying questions if needed
        5. Be helpful and informative
        6. Remember context from the conversation
        
        If you need to access specific information from a database or external service,
        indicate what type of information you need and I'll help you retrieve it.
        """
    
    def process_text(self, text: str, user_id: str, session_id: str, 
                    conversation_history: list = None) -> Optional[str]:
        """
        Process user input text and generate appropriate response
        """
        try:
            # Build conversation messages
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history if available
            if conversation_history:
                for record in conversation_history[-5:]:  # Last 5 exchanges
                    messages.append({"role": "user", "content": record.text_input})
                    messages.append({"role": "assistant", "content": record.text_response})
            
            # Add current user input
            messages.append({"role": "user", "content": text})
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                user=f"{user_id}_{session_id}"
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error in LLM processing: {e}")
            return "I'm sorry, I encountered an error processing your request. Please try again."
    
    def analyze_intent(self, text: str) -> Dict[str, Any]:
        """
        Analyze user intent and extract entities
        """
        try:
            intent_prompt = f"""
            Analyze the following user input and extract:
            1. Intent (e.g., question, request, command, greeting, etc.)
            2. Entities (names, dates, locations, etc.)
            3. Confidence level (high, medium, low)
            4. Required actions or information needed
            
            User input: "{text}"
            
            Respond in JSON format:
            {{
                "intent": "intent_type",
                "entities": {{"entity_type": "entity_value"}},
                "confidence": "confidence_level",
                "actions_needed": ["action1", "action2"],
                "info_needed": ["info1", "info2"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": intent_prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            # Parse JSON response
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Error in intent analysis: {e}")
            return {
                "intent": "unknown",
                "entities": {},
                "confidence": "low",
                "actions_needed": [],
                "info_needed": []
            }
    
    def generate_response_with_context(self, text: str, context_data: Dict[str, Any], 
                                     user_id: str, session_id: str) -> Optional[str]:
        """
        Generate response using additional context data from database or external sources
        """
        try:
            context_prompt = f"""
            User query: "{text}"
            
            Available context data:
            {json.dumps(context_data, indent=2)}
            
            Using the provided context, generate a helpful and natural response to the user's query.
            Keep the response conversational and suitable for speech output.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": context_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                user=f"{user_id}_{session_id}"
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error in context-aware response generation: {e}")
            return "I'm sorry, I couldn't process your request with the available information."
    
    def summarize_conversation(self, conversation_history: list) -> str:
        """
        Generate a summary of the conversation history
        """
        try:
            if not conversation_history:
                return "No conversation history available."
            
            # Prepare conversation text
            conversation_text = ""
            for record in conversation_history:
                conversation_text += f"User: {record.text_input}\n"
                conversation_text += f"Assistant: {record.text_response}\n\n"
            
            summary_prompt = f"""
            Summarize the following conversation in 2-3 sentences:
            
            {conversation_text}
            
            Focus on the main topics discussed and any important information exchanged.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": summary_prompt}],
                max_tokens=100,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error in conversation summarization: {e}")
            return "Unable to summarize conversation."

# Singleton instance
llm_processor = LLMProcessor()
