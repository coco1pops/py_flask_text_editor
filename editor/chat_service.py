import google.auth
from google.auth.transport.requests import Request

import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from google.auth.exceptions import DefaultCredentialsError

import os
import logging

# --- Global instance of the ChatService ---
chat_service_instance = None # Initialize to None

# --- Function to initialize the global instance ---
def initialize_global_chat_service():

    global chat_service_instance
    try:
        chat_service_instance = ChatService()
        logging.debug(f"Global ChatService instance created.")
    except (ValueError, RuntimeError) as e:
        logging.exception(f"CRITICAL ERROR: Failed to initialize ChatService module: {e}")
        chat_service_instance = None # Ensure it's None if initialization fails

# --- Helper function to get the instance ---
def get_chat_service():
    """
    Provides access to the globally initialized ChatService instance.
    Returns None if initialization failed.
    """
    return chat_service_instance

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
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},]
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
            response_text = response.text
            logging.debug(f"Received model response: {response_text[:30]}")
            return response_text
        except Exception as e:
            logging.error(f"Error sending message: {e}")
            raise

    def get_chat_history(self):
        """
        Returns the current conversation history.
        """
        if self.chat_session is None:
            return []
        return self.chat_session.history

    def reset_chat(self, systemInstruction):
        """
        Clears the current chat session and starts a new one.
        """
        logging.debug("Resetting chat session...")
        self.chat_model = genai.GenerativeModel(
                model_name='gemini-2.5-flash-lite',
                generation_config=self.generation_config,
                system_instruction=systemInstruction,
                safety_settings=self.safety_settings
                )
        self.chat_session = self.chat_model.start_chat(history=[])
        logging.debug("Chat session reset.")
    
    def add_history(self, creator, message):
        """
        Adds a record to the chat history   
        """
        content=[]
        content.append(message)
        logging.debug("Adding message to history")
        try:
            self.chat_session.history.append ({'role': creator, 'parts' : content})
        except Exception as e:
            logging.error (f"Failed to append to chat history {e}")