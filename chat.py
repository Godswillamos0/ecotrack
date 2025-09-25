from groq import Groq
from dotenv import load_dotenv
import os

# Load API key from .env
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Pre-prompt using LangChain style system message
SYSTEM_PROMPT = """
You are EcoTrack, an AI assistant that helps users understand their carbon footprint.  
Your job is to:
1. Analyze the user’s described activities (like transport, diet, energy use).  
2. Estimate a carbon score in grams of CO2 equivalent (CO2e).  
3. Provide 2–7 actionable, ecology-focused tips to reduce their footprint.  

⚠️ Important rules:  
- Only talk about ecology, sustainability, and carbon safety.  
- Do not answer unrelated questions (politics, sports, etc.). Politely remind the user you only handle green and eco topics.  
- Always structure responses in this format:

Based on your activities, your estimated carbon score is **<NUMBER>g CO2e**.

Here are some suggestions to reduce your footprint:
1. ...
2. ...
3. ...
.. ...
"""

def generate_response(user_input: str) -> str:
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7,
        max_completion_tokens=2048,
        top_p=1,
        reasoning_effort="medium",
        stream=True,
    )

    # Collect streamed output
    response_chunks = []
    for chunk in completion:
        if chunk.choices[0].delta.content:
            response_chunks.append(chunk.choices[0].delta.content)

    return "".join(response_chunks)

# Example usage
if __name__ == "__main__":
    prompt = "I drove to work, ate a beef burger for lunch, and used electricity for 8 hours."
    result = generate_response(prompt)
    print(result)

