from openai import OpenAI

import os
key = os.getenv("openai")
client = OpenAI(api_key=key)  # Automatically reads API key from the environment
def chat_with_gpt():

    
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "stop"]:
            print("Goodbye!")
            break
        
        conversation.append({"role": "user", "content": user_input})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            temperature=0.7,
            max_tokens=300
        )
        
        reply = response.choices[0].message.content
        print(f"ChatGPT: {reply}\n")
        
        conversation.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    chat_with_gpt()
