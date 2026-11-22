
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

print("Connecting to Gemini...")

try:
    response = client.interactions.create(
        model="gemini-3.8-flash",
        input="Explain phishing detection in two sentences.",
        timeout=60
    )

    print("\nSUCCESS!")
    print(response.output_text)

except Exception as e:
    print("\nAPI ERROR:", repr(e))
