def handle_techy(history):
    # Hier kommt dein Techy-spezifischer Code rein
    history.append({"role": "assistant", "content": "Techy mode active. How can I help you?"})
    return history

if __name__ == "__main__":
    handle_techy()