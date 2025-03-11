from openai import OpenAI
import os

key = os.getenv("openai")
client = OpenAI(api_key=key)  # Automatically reads API key from the environment

def chat_with_gpt():
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "system", "content": "You are now analyzing the likelihood of a lettuce plant being diseased. Based on the input, provide a score from 0 to 1, where 1 is certainly diseased and 0 is certainly healthy. If the score is above 0.5, output a message indicating that the plant is likely diseased."}
    ]
    
    while True:
        # Specific input about the lettuce plant's condition and the image path
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "stop"]:
            print("Goodbye!")
            break
        
        # Include the local image file path in the conversation
        image_path = os.path.join(os.getcwd(), "lettuce_image.jpg")  # Assuming the image is in the same directory
        user_message = f"{user_input} Here is the local path to the image of the plant: {image_path}"
        
        conversation.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            temperature=0.7,
            max_tokens=300
        )
        
        reply = response.choices[0].message.content
        
        # Extract the score from the response to determine if the lettuce is diseased
        try:
            score = float(reply)
            if 0 <= score <= 1:
                print(f"Likelihood of disease: {score}")
                if score > 0.5:
                    print("The lettuce is likely diseased. Please investigate further.")
            else:
                print("Invalid response.")
        except ValueError:
            print("Invalid response.")

        conversation.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    chat_with_gpt()
