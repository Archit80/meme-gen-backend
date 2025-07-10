
Full file again (for reference):

import google.generativeai as genai
import base64
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

MEME_PROMPT = "Write a short and funny meme caption for this image."

def image_to_gemini_payload(image_bytes):
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    return {
        "inline_data": {
            "mime_type": "image/jpeg",
            "data": base64_image
        }
    }

def generate_meme_text(image_bytes):
    model = genai.GenerativeModel("gemini-pro-vision")
    image_payload = image_to_gemini_payload(image_bytes)
    
    response = model.generate_content(
        [MEME_PROMPT, image_payload]
    )

    return response.text.strip()

🔍 Line-by-Line Breakdown
1–4: 🔧 Importing Stuff

import google.generativeai as genai

    This imports the Gemini SDK and renames it genai so we can use shorter syntax like genai.configure(...).

import base64

    Standard Python library to convert image bytes into base64 strings, which Gemini Vision understands.

import os

    Lets us access environment variables, like your Gemini API key stored in .env.

from dotenv import load_dotenv

    Imports a helper to load .env file values into your app, so you don’t hardcode secrets.

5–6: 🔐 Load API Key

load_dotenv()

    Finds your .env file and loads the variables inside it into your Python environment.

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    Passes your Gemini API key to the SDK using the env variable.

8: 🎯 Set the prompt

MEME_PROMPT = "Write a short and funny meme caption for this image."

    This is the instruction prompt we’ll send to Gemini, alongside the image.

    You can customize this to make captions serious, sarcastic, edgy, etc.

10–14: 🖼️ Convert image → Gemini format

def image_to_gemini_payload(image_bytes):

    Defines a function that takes raw image data (in bytes), and prepares it for Gemini.

    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    Converts those raw bytes into a base64-encoded string, and decodes from b'...' to a regular string.

    Gemini needs this format to understand images.

    return {
        "inline_data": {
            "mime_type": "image/jpeg",
            "data": base64_image
        }
    }

    Wraps the base64 image inside the format Gemini expects, with:

        "mime_type" = tells it what kind of file it is

        "data" = your image, encoded as base64

16–22: 🧠 Generate Meme Text from Image

def generate_meme_text(image_bytes):

    Defines the main function that takes in the uploaded image and returns a funny caption.

    model = genai.GenerativeModel("gemini-pro-vision")

    Creates an instance of Gemini Vision model, capable of understanding both image and text.

    image_payload = image_to_gemini_payload(image_bytes)

    Converts the uploaded image into base64 + wrapped format using the function we made earlier.

    response = model.generate_content(
        [MEME_PROMPT, image_payload]
    )

    This is the ✨ magic call ✨:

        Sends both the prompt and the image to Gemini

        Gemini “sees” the image, reads the prompt, and replies with a caption

    return response.text.strip()

    Grabs only the text part of the response (the meme caption) and removes any trailing whitespace.

🔁 Summary of Flow

Image bytes 🖼️
   ↓
Convert to base64 🧪
   ↓
Send to Gemini (prompt + image) 🤖
   ↓
Gemini returns caption 📝
   ↓
You slap that caption on the image with Pillow 🎨

💡 Pro Tip: Test this in isolation

You can test generate_meme_text() by reading a file like this:

with open("test_image.jpg", "rb") as f:
    caption = generate_meme_text(f.read())
    print("CAPTION:", caption)