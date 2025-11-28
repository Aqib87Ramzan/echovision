from inference_sdk import InferenceHTTPClient
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Read API key from environment variable
API_KEY = os.getenv("CURRENCY_NOTES_API")
if not API_KEY:
    raise ValueError("Currency notes API key not set in .env file!")

# Initialize Roboflow client using the API key from .env
CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=API_KEY  # <-- use the variable, not the string
)


# Mapping of model class names to human-friendly labels
LABEL_MAP = {
    "10rs": "10 rupee note",
    "20rs": "20 rupee note",
    "50rs": "50 rupee note",
    "100rs": "100 rupee note",
    "500rs": "500 rupee note",
    "1000rs": "1000 rupee note",
    "5000rs": "5000 rupee note"
}

def detect_currency(image):
    """
    Runs both currency detection models (v1 and v2) and returns 
    the best prediction (highest confidence) with a friendly label.

    `image` can be either:
    - a file path (str)
    - a NumPy array (cv2 image)
    """
    r1 = CLIENT.infer(image, model_id="currency-identification-smart-glasses/1")
    r2 = CLIENT.infer(image, model_id="currency-identification-smart-glasses/2")

    predictions1 = r1.get("predictions", [])
    predictions2 = r2.get("predictions", [])

    if not predictions1 and not predictions2:
        return None

    best1 = max(predictions1, key=lambda x: x["confidence"]) if predictions1 else None
    best2 = max(predictions2, key=lambda x: x["confidence"]) if predictions2 else None

    if best1 and best2:
        best = best1 if best1["confidence"] > best2["confidence"] else best2
    else:
        best = best1 or best2

    class_name = best.get("class", "").lower()
    friendly_label = LABEL_MAP.get(class_name, class_name)
    best["friendly_label"] = friendly_label

    return best  # <— THIS MUST RETURN the prediction
