def handle_business(messages):
    # Adjust the messages for business users
    for message in messages:
        if message["role"] == "user":
            message["content"] = f"[Business User]: {message['content']}"
    return messages

def format_business_response(response):
    # Format the response specifically for business users
    return f"Business Insight: {response}"

def is_business_user(user_profile):
    # Logic to determine if the user is a business person
    return user_profile.get("role") == "business" or user_profile.get("it_knowledge") == "limited"

def process_business_mode(messages, user_profile):
    if is_business_user(user_profile):
        messages = handle_business(messages)
        response = generate_business_response(messages)
        return format_business_response(response)
    else:
        return "User profile does not match business criteria." 

def generate_business_response(messages):
    # Placeholder for generating a response based on business messages
    return "This is a response tailored for business users."