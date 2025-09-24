def determine_user_profile(user_message):
    technical_keywords = [
        "code", "algorithm", "script", "model", "dataset", "pipeline", "runtime", "compute", "integration",
        "orchestration", "deployment", "configuration", "installation", "debugging", "api", "sdk", "cli",
        "container", "cluster", "credentials", "token", "logs", "error", "stack trace",
        "technical", "tech", "developer", "engineer", "programming", "software", "hardware"
    ]
    technical_starts = [
        "how to run", "how to configure", "how to install", "how to fix", "how to integrate",
        "how to debug", "how to upload", "how to execute"
    ]

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

    is_technical_start = any(user_message_lower.startswith(s) for s in technical_starts)
    is_business_start = any(user_message_lower.startswith(s) for s in business_starts)

    has_technical = any(kw in user_message_lower for kw in technical_keywords)
    has_business = any(kw in user_message_lower for kw in business_keywords)

    # Tie-break rule
    if has_technical and has_business:
        if any(kw in user_message_lower for kw in ["cost", "pricing", "license"]):
            return "Business"
        return "Technical"
    if is_technical_start or has_technical:
        return "Technical"
    if is_business_start or has_business:
        return "Business"
    # If the message contains "technical" or "tech", classify as Technical
    if "technical" in user_message_lower or "tech" in user_message_lower:
        return "Technical"
    return "Business"

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