from openai import OpenAI
import os

key = os.getenv("openai")
client = OpenAI(api_key=key)  # Automatically reads API key from the environment

def chat_with_gpt():
    while True:
        user_input = input("Enter a message (or type 'exit' to quit): ")
        
        if user_input.lower() in ["exit", "quit", "stop"]:
            print("Goodbye!")
            break
        
        print(f"You said: {user_input}")

if __name__ == "__main__":
    chat_with_gpt()
