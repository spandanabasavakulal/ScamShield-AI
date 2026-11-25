
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("API key not found!")

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        timeout=120000
    )
)

print("Sending request to Gemini...")

try:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="Explain phishing detection in two sentences."
    )

    print("\nSUCCESS!")
    print(response.text)

except Exception as e:
    print("\nERROR:", repr(e))

finally:
    client.close()
