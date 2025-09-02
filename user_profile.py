import openai
import os

class UserProfile:
    def __init__(self):
        self.profile = None

    def determine_user_profile(user_message):
        # Technical (Physicist) keywords and sentence starters
        technical_keywords = [
            "code", "algorithm", "script", "model", "dataset", "pipeline", "runtime", "compute", "integration",
            "orchestration", "deployment", "configuration", "installation", "debugging", "api", "sdk", "cli",
            "container", "cluster", "credentials", "token", "logs", "error", "stack trace"
        ]
        technical_starts = [
            "how to run", "how to configure", "how to install", "how to fix", "how to integrate",
            "how to debug", "how to upload", "how to execute"
        ]

        # Business keywords and sentence starters
        business_keywords = [
            "cost", "pricing", "roi", "license", "contract", "subscription", "procurement", "compliance",
            "gdpr", "roadmap", "onboarding", "support", "training", "usability", "stakeholder adoption",
            "decision-making", "value", "plan", "business impact", "management", "long-term benefit"
        ]
        business_starts = [
            "what is the cost", "what is the license", "what is the support", "what is the roadmap",
            "what is the value", "what is the plan", "what is the business impact"
        ]

        user_message_lower = user_message.lower().strip()

        # Check for sentence starters
        is_technical_start = any(user_message_lower.startswith(s) for s in technical_starts)
        is_business_start = any(user_message_lower.startswith(s) for s in business_starts)

        # Check for keywords
        has_technical = any(kw in user_message_lower for kw in technical_keywords)
        has_business = any(kw in user_message_lower for kw in business_keywords)

        # Tie-break rule
        if has_technical and has_business:
            # If pricing/cost/license is the focus, classify as Business
            if any(kw in user_message_lower for kw in ["cost", "pricing", "license"]):
                return "Business"
            return "Technical"  # Physicist persona
        if is_technical_start or has_technical:
            return "Technical"
        if is_business_start or has_business:
            return "Business"
        # Ambiguous or generic: classify as Business
        return "Business"

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