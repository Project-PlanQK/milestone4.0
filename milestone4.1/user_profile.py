import json
import openai
import os

class UserProfile:
    def __init__(self):
        self.profile = None

    def determine_user_profile(self, user_message):  # Add user_message parameter
        """
        Determines the user profile based on the message content.
        Args:
            user_message (str): The message from the user to analyze
        Returns:
            str: The determined profile ("technical" or "business")
        """
        # Call additional language model to analyze the user message
        response = self.call_language_model(user_message)

        if isinstance(response, dict) and "profile" in response:
            self.profile = response["profile"]
        else:
            # Default to business profile if unable to determine
            self.profile = "business"
            
        return self.profile

    def call_language_model(self, user_message):
        try:
            client = openai.AzureOpenAI(
                api_key = os.getenv("AZURE_OPENAI_API_KEY"),
                endpoint = os.getenv("ENDPOINT_URL"),
                api_version="2025-01-01-preview"
            )
            
            # Import keywords from utils.py
            from utils import technical_keywords, business_keywords, technical_starts, business_starts
            
            # Create a prompt that includes the keywords
            system_prompt = f"""
            You are a user profile classifier. Analyze the message and classify the user as either technical or business oriented.

            Technical indicators:
            - Keywords: {', '.join(technical_keywords)}
            - Common phrases: {', '.join(technical_starts)}

            Business indicators:
            - Keywords: {', '.join(business_keywords)}
            - Common phrases: {', '.join(business_starts)}

            Rules:
            1. If the message contains technical terms or implementation details -> technical.
            2. If the message focuses on business value or costs -> business.
            3. In case of ambiguity, prefer technical if code/implementation is mentioned.
            4. In case of no clear indicators, default to business.

            Respond ONLY with the word "technical" or "business".
            """

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3, #präzise, vorhersehbare und konsistente Antwort mit niedriger temperatur
                max_tokens=10
            )
            
            # Get the profile directly from the response
            profile = response.choices[0].message.content.strip().lower()
            
            # Ensure only valid responses
            if profile not in ["technical", "business"]:
                profile = "business"
                
            return {"profile": profile}
                
        except Exception as e:
            print(f"Error in profile determination: {e}")
            return {"profile": "business"}
      
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