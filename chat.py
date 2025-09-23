from groq import Groq
from dotenv import load_dotenv
import os

# Load API key from .env
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_response(user_input: str) -> str:
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": user_input}],
        temperature=1,
        max_completion_tokens=8192,
        top_p=1,
        reasoning_effort="medium",
        stream=True,
        stop=None
    )

    # Collect output instead of printing
    response_chunks = []
    for chunk in completion:
        if chunk.choices[0].delta.content:
            response_chunks.append(chunk.choices[0].delta.content)

    return "".join(response_chunks)

# # Example usage:
# result = generate_response("Write a short poem about the sunrise.")
# print(result)


if __name__ == "__main__":
    generate_response("Hello, how are you?")
