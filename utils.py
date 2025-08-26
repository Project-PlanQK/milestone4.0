def determine_user_profile(user_message):
    # Simple keyword-based profiling logic
    business_keywords = ["business", "manager", "finance", "strategy", "market"]
    tech_keywords = ["technical", "developer", "IT", "software", "engineering"]

    user_message_lower = user_message.lower()

    if any(keyword in user_message_lower for keyword in business_keywords):
        return "Business"
    elif any(keyword in user_message_lower for keyword in tech_keywords):
        return "Technical"
    else:
        return "Unknown"

def adjust_response_based_on_profile(profile, response):
    # Adjust the response based on the identified user profile
    if profile == "Business":
        return f"[Business Mode] {response}"
    elif profile == "Technical":
        return f"[Technical Mode] {response}"
    else:
        return response  # Default response if profile is unknown

def extract_relevant_information(messages):
    # Extract relevant information from the conversation history
    return [msg['content'] for msg in messages if msg['role'] == 'user']