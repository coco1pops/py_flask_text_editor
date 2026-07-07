from email import message

import google.auth

from google import genai
from google.genai import types

from editor.models.params import ModelsService

from google.genai.types import GenerateContentConfig

from dataclasses import dataclass

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
def initialize_global_chat_service(project):

    global chat_service_instance
    try:
        logging.debug(f"Initializing global ChatService instance with project: {project}")
        chat_service_instance = ChatService(
            vertexai=True,
            project=project
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

# 
# Class to access LLM chat services. It manages the chat session, including the model, contents, and clients.
#
class ChatService:

    def __init__(self, project, vertexai=False):
        try:
            self.project=project
            self.vertexai=vertexai
            # Initialise private properties for model, contents, and clients
            self._chat_config=GenerateContentConfig()
            self._model=None
            self._location=None
            self._contents=[]
            self._clients={}

        except Exception as e:
            logging.exception(f"CRITICAL ERROR: Failed to initialize ChatService: {e}")
            raise RuntimeError(f"Failed to initialize ChatService: {e}")
#
# (PRIVATE) Lazily provisions or retrieves the correct client for the target location.
#
    def _get_client(self, location: str) -> genai.Client:
        
        if location not in self._clients:
            self._clients[location] = genai.Client(
                vertexai=self.vertexai,
                project=self.project,
                location=location,
                http_options=types.HttpOptions(
                    retry_options=types.HttpRetryOptions(
                    attempts=4,        # Set your max retry attempts here
                    initial_delay=1,   # Optional: initial backoff delay in seconds
                    max_delay=10       # Optional: maximum backoff delay
                    )
                )
            )
        return self._clients[location]
#
# Sends a user message to the chat session and returns the model's response.
#
    def send_message(self, message: str) -> str:

        if not message:
            return "Please provide a message."

        try:
            logging.debug(f"Sending user prompt...")
            self.add_history("user", message)

            client = self._get_client(self._location)
            response = client.models.generate_content(model=self._model, contents=self._contents, config=self._chat_config)
            if not response.candidates:
                return self._process_no_candidates(response)
            else:
                return self._process_response(response)          
       
        except Exception as e:

            return self._handle_send_exception(e)


            raise
#
# (PRIVATE) Processes the case where no candidates are returned from the model, logging the reason and returning a 
# structured ChatResult. 
#
    def _process_no_candidates(self, response):
        reason_str = "UNKNOWN"
        if hasattr(response, "prompt_feedback") and response.prompt_feedback:
            feedback = response.prompt_feedback

            # Safely normalize the block reason enum/string
            reason = getattr(feedback, "block_reason", "UNKNOWN")
            reason_str = getattr(reason, "name", str(reason)).upper()
        logging.error("No candidates returned from the model: %s", reason_str)

        return ChatResult(False, reason_str, "NO_CANDIDATES", "")
#
# (PRIVATE) Processes the model's response, checking the finish reason and handling safety errors or other issues accordingly.
#    
    def _process_response(self, response):
        candidate = response.candidates[0]
        result = ChatResult(False, "", "", "")

        reason_id = candidate.finish_reason
        finish_reason = getattr(reason_id, "name", str(reason_id)).upper()
        logging.debug(f"Finish reason: {finish_reason}")

        if reason_id == "STOP":
            result.success = True
            result.text = response.text

        elif reason_id == "SAFETY":
            logging.debug(f"Processing safety error for candidate with finish reason: {finish_reason}")
            result = self._process_safety_error(candidate)
        else:
            result.text = f"Failed to generate content. Finish reason: {finish_reason}"

        return result
#
# (PRIVATE) Processes exceptions that occur during the send_message operation, logging details and returning a structured ChatResult.
# If safety or block reasons are detected, it handles them accordingly. Otherwise, it logs the exception details and 
# re-raises the exception.
#
    def _handle_send_exception(self, e):
        logging.exception("Exception occurred while sending message to the model: %s", e)
        candidate=e.args[0]
        
        if hasattr(candidate, "finish_reason"):
            reason_id = candidate.finish_reason
            finish_reason = getattr(reason_id, "name", str(reason_id)).upper()
            logging.debug(f"Finish reason: {finish_reason}")
            if finish_reason == "SAFETY":

                result=self._process_safety_error(candidate)

            else:
                result.text = f"Failed to generate content. Finish reason: {finish_reason}"

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

    def _process_safety_error(self, candidate):
        result=ChatResult(False,"Gemini rejected the prompt: ","SAFETY","")

        reasons=[]
        for rating in candidate.safety_ratings:
            if getattr(rating, "blocked", False):
                reasons.append(
                    f" Blocked category: {rating.category} (Probability: {rating.probability}) "
                )

            result.safety_ratings = ", ".join(reasons)

        return result
#
# Clears the current chat session and starts a new one, essentially preparing the model, location and chat configuration 
# for a new conversation based on the provided story and optional override instruction.
#    
    def reset_chat(self, story, override=None):

        logging.debug("Resetting chat session...")

        if override:
            instruction=override
        else:
            instruction=story.systeminstruction

        if instruction == "" or instruction == "None":
            instruction=None

        self._model=story.model
        self._location=ModelsService.get_model(story.model).location

        self._chat_config.system_instruction = instruction    
        self._chat_config.temperature = story.temperature
        self._chat_config.top_p = story.top_p
        self._chat_config.safety_settings =  [
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold=story.harassment_threshold),
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold=story.hate_speech_threshold),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold=story.explicit_content_threshold),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold=story.dangerous_content_threshold),]
        # Not used for now, but can be set to control when the model stops generating text
        self._chat_config.stop_sequences = []
        self._contents=[]
        logging.debug("Chat session reset.")
#
# Adds a record to the chat history. Copes with strings, lists of dicts with either text or image_mime_type and image_data keys.
#    
    def add_history(self, creator, message):

        logging.debug(f"Adding single message to history: {message}")
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
            self._contents.append(
                types.Content(
                    role=creator, # "user" or "model"
                    parts=api_parts
                )
            )

        except Exception as e:
            logging.error (f"Failed to append to chat history {e}")
            raise