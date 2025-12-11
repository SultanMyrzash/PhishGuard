from google import genai
from google.genai import types
from openai import OpenAI
from .config import SystemConfig
import io
import base64

class AIEngine:
    """
    The Intelligence Layer.
    Orchestrates requests to Google Gemini (Cloud) and LM Studio (Local).
    """

    def __init__(self):
        # Initialize Google Client (Lazy loading to prevent crash if no key)
        self.google_client = None
        if SystemConfig.GOOGLE_API_KEY:
            self.google_client = genai.Client(api_key=SystemConfig.GOOGLE_API_KEY)

    def _pil_to_bytes(self, pil_image):
        """Helper: Convert PIL image to bytes for Google API."""
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()

    def _pil_to_base64(self, pil_image):
        """Helper: Convert PIL image to Base64 for Local/OpenAI API."""
        buffered = io.BytesIO()
        pil_image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def analyze(self, model_key, text_data=None, image_data=None, mode="SINGLE"):
        """
        Main execution method.
        
        Args:
            model_key (str): The specific key from SystemConfig.MODELS
            text_data (str): Parsed email headers/body
            image_data (PIL.Image): Screenshot
            mode (str): "SINGLE" (Deep Scan) or "COMPARE" (Concise)
        """
        # 1. Validation & Config Lookup
        if model_key not in SystemConfig.MODELS:
            return f"❌ Configuration Error: Model '{model_key}' not found."
            
        conf = SystemConfig.MODELS[model_key]
        provider = conf['provider']
        model_name = conf['model_name']
        
        # 2. Select Prompt based on Mode
        system_prompt = SystemConfig.PROMPT_SINGLE if mode == "SINGLE" else SystemConfig.PROMPT_COMPARE

        try:
            # ==========================================
            # STRATEGY A: GOOGLE GEMINI (Cloud)
            # ==========================================
            if provider == "GOOGLE":
                if not self.google_client:
                    return "❌ Error: GEMINI_API_KEY not found in .env file."

                # Build Content Parts
                parts = [types.Part.from_text(text=system_prompt)]
                
                if text_data:
                    parts.append(types.Part.from_text(text=f"EVIDENCE ARTIFACTS:\n{text_data}"))
                
                if image_data:
                    img_bytes = self._pil_to_bytes(image_data)
                    parts.append(types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"))
                    parts.append(types.Part.from_text(text="[Attached Visual Evidence]"))

                # Configure Tools (Google Search) - Only for Deep Scans
                tools = []
                if mode == "SINGLE":
                    tools = [types.Tool(google_search=types.GoogleSearch())]

                # Execute Request
                response = self.google_client.models.generate_content(
                    model=model_name,
                    contents=[types.Content(role="user", parts=parts)],
                    config=types.GenerateContentConfig(tools=tools, temperature=0.3)
                )
                
                # Handle cases where response is blocked or empty
                if not response.text:
                    return "⚠️ AI returned no text (Possible Safety Filter Trigger)."
                return response.text

            # ==========================================
            # STRATEGY B: LOCAL LLM (LM Studio)
            # ==========================================
            elif provider == "LOCAL":
                client = OpenAI(base_url=SystemConfig.LOCAL_BASE_URL, api_key=SystemConfig.LOCAL_API_KEY)
                
                messages = [{"role": "system", "content": system_prompt}]
                
                user_content = []
                if text_data:
                    user_content.append({"type": "text", "text": f"EVIDENCE:\n{text_data}"})
                
                if image_data:
                    # Check capabilities defined in config
                    if "vision" in conf['capabilities']:
                        b64_img = self._pil_to_base64(image_data)
                        user_content.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}
                        })
                    else:
                        user_content.append({"type": "text", "text": "[NOTE: Image uploaded but ignored (Model is Text-Only).]"})
                
                messages.append({"role": "user", "content": user_content})

                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.2
                )
                return response.choices[0].message.content

        except Exception as e:
            return f"⚠️ Inference Error ({provider}): {str(e)}"