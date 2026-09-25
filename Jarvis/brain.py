import os
from dotenv import load_dotenv
from google import genai
import warnings

# Suppress all warnings
warnings.filterwarnings("ignore")

# Load variables from .env
load_dotenv()

# Get API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# --------------------------------------------------
# AI Clients
# --------------------------------------------------

openai_client = None
gemini_client = None

if OPENAI_API_KEY:
    from openai import OpenAI

    openai_client = OpenAI(api_key=OPENAI_API_KEY)

if GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)


# --------------------------------------------------
# Select AI provider
# --------------------------------------------------

if GEMINI_API_KEY:
    PROVIDER = "gemini"
elif OPENAI_API_KEY:
    PROVIDER = "openai"
else:
    raise RuntimeError(
        "No API key found. Add OPENAI_API_KEY or GEMINI_API_KEY "
        "to your .env file."
    )


# --------------------------------------------------
# Models
# --------------------------------------------------

OPENAI_MODEL = "gpt-4o-mini"
GEMINI_MODEL = "gemini-3.6-flash"


# --------------------------------------------------
# Jarvis personality
# --------------------------------------------------

SYSTEM_PROMPT = """
You are Jarvis, a personal AI assistant.

Your personality:
- intelligent
- calm
- helpful
- concise
- friendly
- professional

Answer the user's question clearly.

If the user asks something technical,
explain it step by step.

If you don't know something,
say so instead of inventing information.
"""


# --------------------------------------------------
# Conversation memory
# --------------------------------------------------

conversation = []


# --------------------------------------------------
# OpenAI
# --------------------------------------------------

def ask_openai(messages):
    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages
    )

    return response.choices[0].message.content


# --------------------------------------------------
# Gemini
# --------------------------------------------------

def ask_gemini(messages):
    # Convert OpenAI-style messages into Gemini format
    contents = []

    for message in messages:
        role = message["role"]
        content = message["content"]

        if role == "system":
            continue

        # Gemini uses "user" and "model"
        gemini_role = "model" if role == "assistant" else "user"

        contents.append({
            "role": gemini_role,
            "parts": [
                {"text": content}
            ]
        })

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config={
            "system_instruction": SYSTEM_PROMPT
        }
    )

    return response.text


# --------------------------------------------------
# Main Jarvis function
# --------------------------------------------------

def ask_jarvis(user_message):

    # Add user's message
    conversation.append({
        "role": "user",
        "content": user_message
    })

    # Build messages for OpenAI
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        *conversation
    ]

    # Use whichever provider has an available key
    try:
        if PROVIDER == "openai":
            answer = ask_openai(messages)
        elif PROVIDER == "gemini":
            answer = ask_gemini(messages)
        else:
            answer = "No AI provider available"
    except Exception as e:
        # Fallback to Gemini if OpenAI fails
        if PROVIDER == "openai" and gemini_client:
            print(f"OpenAI error: {str(e)[:50]}... Falling back to Gemini...")
            answer = ask_gemini(messages)
        else:
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                raise RuntimeError(
                    "Gemini API quota is exhausted. Wait for the quota reset "
                    "or enable billing/use another Gemini project."
                )
            raise RuntimeError(f"AI provider error: {str(e)}")

    # Save Jarvis's answer
    conversation.append({
        "role": "assistant",
        "content": answer
    })

    return answer
