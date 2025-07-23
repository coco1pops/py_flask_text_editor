import google.generativeai as genai
import google.auth
from google.auth.exceptions import DefaultCredentialsError # For specific error handling

# Path to your downloaded service account JSON key
SERVICE_ACCOUNT_FILE_PATH = "big-pact-460610-j7-63b0aadaba1f.json"

# --- Load Credentials ---
credentials = None
try:
    # Attempt to load credentials from the specified service account file
    credentials, project_id = google.auth.load_credentials_from_file(SERVICE_ACCOUNT_FILE_PATH)
    print(f"Successfully loaded credentials from '{SERVICE_ACCOUNT_FILE_PATH}'")

    # If you are running this on Google Cloud infrastructure (e.g., GCE, Cloud Run),
    # google.auth.load_credentials_from_file() might not be needed if ADC are automatically available.
    # In that case, you could simply rely on:
    # credentials, project_id = google.auth.default()

except FileNotFoundError:
    print(f"Error: Service account file '{SERVICE_ACCOUNT_FILE_PATH}' not found.")
    credentials = None
except DefaultCredentialsError:
    print("Error: Could not automatically find default credentials.")
    print("Ensure GOOGLE_APPLICATION_CREDENTIALS environment variable is set,")
    print("or the service account file is correctly specified.")
    credentials = None
except Exception as e:
    print(f"An error occurred loading credentials: {e}")
    credentials = None

# --- Configure GenAI with Credentials (if loaded) ---
# The google-generativeai library supports using credentials objects directly
# for authentication, abstracting away the API key.
if credentials:
    try:
        genai.configure(credentials=credentials)
        # You might need to know the project ID associated with the service account
        # if the GenAI SDK requires it for certain operations.
        # The 'project_id' variable from load_credentials_from_file might be useful.
        print("GenAI configured successfully with service account credentials.")
        # You still need to specify a model to use
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
    except Exception as e:
        raise RuntimeError(f"Failed to configure GenAI with service account credentials: {e}")
else:
    # If service account credentials failed to load, you MUST have a fallback,
    # or raise an error because the app cannot authenticate.
    # For this example, we'll raise an error if no credentials are found.
    raise ValueError(
        "GenAI authentication failed. "
        "Could not load service account credentials or find application default credentials."
    )