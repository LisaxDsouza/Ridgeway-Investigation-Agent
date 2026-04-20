import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL")

print(f"Key Prefix: {key[:10]}...")
print(f"Model: {model}")

client = Groq(api_key=key)

try:
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": "Hello, respond with 'OK' if you see this."}
        ]
    )
    print("Response:", completion.choices[0].message.content)
except Exception as e:
    print("Error:", e)
