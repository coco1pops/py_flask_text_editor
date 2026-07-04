import google.auth

from google import genai
from google.genai import types

from google.genai.types import GenerateContentConfig

from dataclasses import dataclass

import os
import logging

@dataclass
class ChatResult:
    success: bool
    text: str | None
    finish_reason: str
    safety_ratings: str

# --- Global instance of the ChatService ---

chat_service_instance = None # Initialize to None

# --- Function to initialize the service  ---
# def initialize_global_chat_service():
def initialize_global_chat_service(project, location):

    global chat_service_instance
    try:
        logging.debug(f"Initializing global ChatService instance with project: {project}, location: {location}")
        chat_service_instance = ChatService(
            vertexai=True,
            project=project,
            location=location
            )
        logging.debug(f"Global ChatService instance created.")
    except (ValueError, RuntimeError) as e:
        logging.exception(f"CRITICAL ERROR: Failed to initialize ChatService module: {e}")
        chat_service_instance = None # Ensure it's None if initialization fails

    return chat_service_instance

# --- Helper function to get the instance ---
def get_chat_service():

    global chat_service_instance
    """
    Provides access to the globally initialized ChatService instance.
    Returns None if initialization failed.
    """

    return chat_service_instance


class ChatService:
    """
    Manages the GenAI chat model, API key configuration, and chat history.
    Allows other modules to send messages and receive responses.
    """
    # Add a parameter to control whether to configure GenAI here
    def __init__(self, project, location, vertexai=False):

        try:
            self.client=genai.Client(project=project, location=location, vertexai=vertexai)
            self.chat_config=GenerateContentConfig()
            self.model=None
            self.contents=[]

        except Exception as e:
            logging.exception(f"CRITICAL ERROR: Failed to initialize ChatService: {e}")
            raise RuntimeError(f"Failed to initialize ChatService: {e}")

    def send_message(self, message: str) -> str:
        """
        Sends a user message to the chat session and returns the model's response.
        """
        if self.model is None:
            raise RuntimeError("Chat model is not initialized.")

        if not message:
            return "Please provide a message."

        try:
            logging.debug(f"Sending user prompt...")
            self.add_history("user", message)
            response = self.client.models.generate_content(model=self.model, contents=self.contents, config=self.chat_config)
            if not response.candidates:
                logging.error("No candidates returned from the model.")
                return ChatResult(False, "", "NO_CANDIDATES", "")
            else:

                candidate=response.candidates[0]
                result=ChatResult(False,"","","")
                reason_id=candidate.finish_reason
               
                if reason_id == "STOP":
                    result.success=True
                    result.text=response.text

                else:
                    result=self.process_safety_error(candidate)

                logging.debug(f"Metadata response: {response.usage_metadata}")
                return result
            
       
        except Exception as e:
            candidate=e.args[0]
            if hasattr(candidate, "finish_reason"):
                if candidate.finish_reason:

                    result=self.process_safety_error(candidate)
                    return result
                
            if hasattr(candidate,"block_reason"):
                if candidate.block_reason:
                    block_id=candidate.block_reason
            
                    result=ChatResult(False,"","","")
                    result.finish_reason="BLOCK: %s" % candidate.BlockReason(block_id).name
                    result.text="Gemini blocked the prompt %s" % candidate
                    return result
                
            logging.exception("Gemini failed to respond")

            logging.error("Exception type: %s", type(e))
            logging.error("args type: %s", type(e.args))
            logging.error("args length: %s", len(e.args))

            for i, arg in enumerate(e.args):
                logging.error("arg[%s] type: %s", i, type(arg))
                logging.error("arg[%s] repr: %r", i, arg)
                logging.error("arg[%s] dir: %s", i, dir(arg))

            raise
        
    def process_safety_error(self,candidate):
        result=ChatResult(False,"","","")
        reason_id=candidate.finish_reason
        if reason_id == "SAFETY":
            result.success=False
            result.text="Gemini rejected the prompt: "
            reasons=[]
            for rating in candidate.safety_ratings:
                if getattr(rating, "blocked", False):
                    reasons.append(
                        f"Blocked category: {rating.category} (Probability: {rating.probability}) "
                    )

                result.safety_ratings = ", ".join(reasons)

        return result
    
    def reset_chat(self, story, override=None):
        """
        Clears the current chat session and starts a new one.
        """
        logging.debug("Resetting chat session...")

        if override:
            instruction=override
        else:
            instruction=story.systeminstruction

        if instruction == "" or instruction == "None":
            instruction=None

        self.model=story.model

        self.chat_config.system_instruction = instruction    
        self.chat_config.temperature = story.temperature
        self.chat_config.top_p = story.top_p
        self.chat_config.safety_settings =  [
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold=story.harassment_threshold),
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold=story.hate_speech_threshold),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold=story.explicit_content_threshold),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold=story.dangerous_content_threshold),]
        # Not used for now, but can be set to control when the model stops generating text
        self.chat_config.stop_sequences = []
        logging.debug("Chat session reset.")
    
    def add_history(self, creator, message):
        """
        Adds a record to the chat history   
        """
        if isinstance(message, list):
            parts = message
        else:
            parts = [{"text": message}]
  
        try:
            api_parts = []
    
            for item in parts:
                if "text" in item:
                    api_parts.append(types.Part.from_text(text=item["text"]))
            
                elif "image_mime_type" in item:
                    # Turn 1 only: The SDK attaches the actual image  here
                    api_parts.append(
                        types.Part.from_bytes(
                            data=item["image_data"],
                            mime_type=item["image_mime_type"]
                        )
                    )

            # Appends the turn into your rolling conversation history
            self.contents.append(
                types.Content(
                    role=creator, # "user" or "model"
                    parts=api_parts
                )
            )

        except Exception as e:
            logging.error (f"Failed to append to chat history {e}")
            raise