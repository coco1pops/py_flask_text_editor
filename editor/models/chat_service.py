import google.auth
from google.auth.transport.requests import Request

import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from google.auth.exceptions import DefaultCredentialsError

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
# TODO: Changing to chat service for every call, so this global instance may not be needed.
# chat_service_instance = None # Initialize to None

# --- Function to initialize the service  ---
# def initialize_global_chat_service():
def initialize_chat_service():
    # TODO: Replacing with chat service for every call, so this global instance may not be needed.
    # global chat_service_instance
    try:
        chat_service_instance = ChatService()
        logging.debug(f"Global ChatService instance created.")
    except (ValueError, RuntimeError) as e:
        logging.exception(f"CRITICAL ERROR: Failed to initialize ChatService module: {e}")
        chat_service_instance = None # Ensure it's None if initialization fails
    # TODO: If you want to keep a global instance, uncomment the following line
    return chat_service_instance

# --- Helper function to get the instance ---
def get_chat_service():
    """
    Provides access to the globally initialized ChatService instance.
    Returns None if initialization failed.
    """
    # TODO: Replacing with chat service for every call, so this global instance may not be needed.
    # return chat_service_instance
    return initialize_chat_service()  # Return a new instance for each call, as per the new design

# Path to your downloaded service account JSON key
SERVICE_ACCOUNT_FILE_PATH = os.getenv("SERVICE_ACCOUNT_FILE_PATH")

class ChatService:
    """
    Manages the GenAI chat model, API key configuration, and chat history.
    Allows other modules to send messages and receive responses.
    """
    # Add a parameter to control whether to configure GenAI here
    def __init__(self):
        self.chat_model = None
        self.chat_session = None
        self.generation_config = None
        self.safety_settings =  [
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},]
        self._initialize()

    def _load_credentials(self):
        # --- Load Credentials ---
        credentials = None
        try:
        #    env_value = os.getenv("ENVIRONMENT")
        #    if env_value and env_value.strip() == "PROD":
        #        logging.info("Chat - Loading Production credentials")

        #        SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

                # Get default credentials and project ID
         #       credentials, project_id = google.auth.default()

                # If credentials need scopes, wrap them
        #        if hasattr(credentials, "with_scopes"):
        #            credentials = credentials.with_scopes(SCOPES)

                # Refresh if needed
         #       credentials.refresh(Request())

         #       logging.debug("Successfully loaded default credentials")
          #  else:
                # Attempt to load credentials from the specified service account file
            logging.info("Chat - Loading  credentials")
            credentials, project_id = google.auth.load_credentials_from_file(SERVICE_ACCOUNT_FILE_PATH)
            logging.debug(f"Successfully loaded credentials from '{SERVICE_ACCOUNT_FILE_PATH}'")

            # If you are running this on Google Cloud infrastructure (e.g., GCE, Cloud Run),
            # google.auth.load_credentials_from_file() might not be needed if ADC are automatically available.
            # In that case, you could simply rely on:
            # credentials, project_id = google.auth.default()

        except FileNotFoundError:
            logging.exception(f"Error: Service account file '{SERVICE_ACCOUNT_FILE_PATH}' not found.")
            credentials = None
        except DefaultCredentialsError:
            logging.exception("Error: Could not automatically find default credentials.")
            logging.exception("Ensure GOOGLE_APPLICATION_CREDENTIALS environment variable is set,")
            logging.exception("or the service account file is correctly specified.")
            credentials = None
        except Exception as e:
            logging.exception(f"An error occurred loading credentials: {e}")
            credentials = None
        return credentials
    
        # --- Configure GenAI with Credentials (if loaded) ---
        # The google-generativeai library supports using credentials objects directly
        # for authentication, abstracting away the API key.


    def _initialize(self):
        """
        Configures GenAI and initializes the chat model and session,
        only if `configure_genai_here` is True.
        """
        # Load the API key if we might need it later, or for debugging.
        # If the library is configured elsewhere, we might not need the key *for configuration*.
        credentials = self._load_credentials()

        if credentials:
            try:
                genai.configure(credentials=credentials)
                # You might need to know the project ID associated with the service account
                # if the GenAI SDK requires it for certain operations.

                logging.debug("GenAI configured successfully with service account credentials.")

                # --- Model Initialization ---
                self.generation_config = GenerationConfig(
                    temperature=1.0,
                    stop_sequences=[])
                
                # This call requires the library to be configured (either here or elsewhere)
                self.chat_model = genai.GenerativeModel(
                    model_name='gemini-2.5-flash-lite',
                    generation_config=self.generation_config
                )

                # Start a new chat session.
                # Note: If the library was configured via credentials, it will use those.
                self.chat_session = self.chat_model.start_chat(history=[])

                logging.debug("ChatService initialized successfully.")

            except Exception as e:
                # This exception will catch errors if the library wasn't configured
                # at all (either locally or externally) when genai.GenerativeModel is called.
             raise RuntimeError(f"Failed to initialize ChatService: {e}")
        else:
            # If service account credentials failed to load, you MUST have a fallback,
            # or raise an error because the app cannot authenticate.
            # For this example, we'll raise an error if no credentials are found.
            raise ValueError(
                "GenAI authentication failed. "
                "Could not load service account credentials or find application default credentials."
            )
        

    def send_message(self, message: str) -> str:
        """
        Sends a user message to the chat session and returns the model's response.
        """
        if self.chat_session is None:
            raise RuntimeError("Chat session is not initialized.")

        if not message:
            return "Please provide a message."

        try:
            logging.debug(f"Sending user prompt...")
            response = self.chat_session.send_message({"role": "user", "parts": message})
            candidate=response.candidates[0]
            result=ChatResult(False,"","","")
            reason_id=candidate.finish_reason
            result.finish_reason=candidate.FinishReason(reason_id).name
            
            if candidate.finish_reason == candidate.FinishReason.STOP:
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
        result.finish_reason=candidate.FinishReason(reason_id).name
        if candidate.finish_reason == candidate.FinishReason.SAFETY:
            result.success=False
            result.text="Gemini rejected the prompt: "
            reasons=[]
            for rating in candidate.safety_ratings:
                if rating.probability > 1:

                    reasons.append(
                        f"{rating}"
                    )

                result.safety_ratings = ", ".join(reasons)
        return result
    
    def get_chat_history(self):
        """
        Returns the current conversation history.
        """
        if self.chat_session is None:
            return []
        return self.chat_session.history

    def reset_chat(self, story, override=None):
        """
        Clears the current chat session and starts a new one.
        """
        logging.debug("Resetting chat session...")

        if override:
            instruction=override
        else:
            instruction=story.systeminstruction

        if instruction == "" or instruction == None:
            instruction="None"

        self.safety_settings =  [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": story.harassment_threshold},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": story.hate_speech_threshold},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": story.explicit_content_threshold},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": story.dangerous_content_threshold},]
        
        self.generation_config = GenerationConfig(
                    temperature=story.temperature,
                    top_p=story.top_p,
                    stop_sequences=[])
        
        self.chat_model = genai.GenerativeModel(
                model_name=story.model,
                generation_config=self.generation_config,
                system_instruction=instruction,
                safety_settings=self.safety_settings
                )
        self.chat_session = self.chat_model.start_chat(history=[])
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
            self.chat_session.history.append ({'role': creator, 'parts' : parts})
        except Exception as e:
            logging.error (f"Failed to append to chat history {e}")
            raise