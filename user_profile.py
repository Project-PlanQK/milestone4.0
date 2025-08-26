import openai
import os

class UserProfile:
    def __init__(self):
        self.profile = None

    def determine_user_profile(self, user_message):
        # Call additional language model to analyze the user message
        response = self.call_language_model(user_message)

        if isinstance(response, dict) and "profile" in response:
            self.profile = response["profile"]
        else:
            # fallback: try to extract from text
            text = response.get("content", "").lower() if isinstance(response, dict) else str(response).lower()
            if "business" in text:
                self.profile = "business"
            elif "technical" in text or "tech" in text:
                self.profile = "technical"
            else:
                self.profile = "unknown"
        return self.profile

    def call_language_model(self, user_message):
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("ENDPOINT_URL")
        openai.api_type = "azure"
        openai.api_key = api_key
        openai.api_base = endpoint
        openai.api_version = "2025-01-01-preview"
        try:
            response = openai.ChatCompletion.create(
                model="your-model-name",  # Replace with the actual model name
                messages=[
                    {"role": "user", "content": user_message}
                ],
                max_tokens=400
            )
            return response.choices[0].message
        except Exception as e:
            print(f"Error calling language model: {e}")
            return {"profile": "unknown"}

    def adjust_response_based_on_profile(self, response):
        if self.profile == "business":
            return self.format_business_response(response)
        elif self.profile == "technical":
            return self.format_technical_response(response)
        else:
            return response  # Default response if profile is unknown

    def format_business_response(self, response):
        # Format the response for business users
        return f"[Business] {response}"

    def format_technical_response(self, response):
        # Format the response for technical users
        return f"[Technical] {response}"