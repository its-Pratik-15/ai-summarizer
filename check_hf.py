import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv('./backend/.env')

token = os.getenv("HF_TOKEN")
if not token:
    print("HF_TOKEN is missing in .env")
    exit(1)

print(f"HF_TOKEN found: {token[:4]}...{token[-4:]}")

client = InferenceClient(api_key=token)
try:
    print("Testing connection...")
    resp = client.chat_completion(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=[{"role": "user", "content": "Say hello in one word."}],
        max_tokens=10
    )
    print("Connection successful!")
    print("Response:", resp.choices[0].message.content)

    # Test summarization
    summary_resp = client.summarization(
        "Usually, summarization models are specific. This is a test text.",
        model="facebook/bart-large-cnn"
    )
    print("Summarization test success:", summary_resp)

except Exception as e:
    print(f"Error: {e}")
