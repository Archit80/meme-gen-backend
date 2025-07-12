import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles


from PIL import Image, ImageDraw, ImageFont
# import textwrap

import cloudinary
import cloudinary.uploader


from uuid import uuid4
import os
from dotenv import load_dotenv
from io import BytesIO


from gemini_utils import generate_meme_text  #AI response
from logger import log_event
from rate_limit import is_allowed, get_usage
from codename_manager import get_or_create_name
from fingerprint_analyzer import get_device_identifier


load_dotenv()  # Load environment variables from .env file

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)



app = FastAPI() 

origins = [
    "http://localhost:5173", #Dev frontend URL
    "https://meme-aunty.vercel.app" #Production frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.mount("/memes", StaticFiles(directory="memes"), name="memes")
#Makes everything in your memes/ folder publicly available at http://localhost:8000/memes/...


@app.get("/")
def hello():
    return {"message": "Hello, World! from FastAPI"}


'''The line @app.get("/") is a decorator. 
It modifies the function that comes after it. 
In this case, it tells FastAPI that the hello function should
handle GET requests for the root path (/)
'''

@app.get("/dummy/")
async def helloji():
    return {"message": "Hello Ji!"}


@app.post("/whoami/")
async def whoami(request: Request):
    try:
        body = await request.json()
        device_token = body.get("device_token")
    except:
        device_token = None

    # Get device identifier using fingerprint analysis
    identifier = get_device_identifier(device_token, request.client.host)
    name = get_or_create_name(identifier)

    return {
        "name": name,
        "credits_left": get_usage(identifier)
    }


@app.get("/reset-quota")
def reset_quota():
    with open("rate_limit.json", "w") as f:
        f.write("{}")
    return {"message": "All quotas reset 🔄"}


#MAIN LOGIC 
@app.post("/generate-meme/")
async def generate_meme(
    file:UploadFile = File(...),
    vibe: str = Form(...),
    device_token: str = Form(None),
    request: Request = None
    ):
 
    # Get device identifier using fingerprint analysis
    identifier = get_device_identifier(device_token, request.client.host)
    
    if not is_allowed(identifier):
        raise HTTPException(status_code=429, detail="You have hit your daily meme limit. Come back tomorrow 👀")
    
    image_bytes = await file.read() #bytes (raw binary data) from the uploaded file
    
    if not image_bytes:
        raise HTTPException(status_code=400, detail="No image uploaded")

    meme_text = generate_meme_text(image_bytes, vibe)
    # Log all entries to a JSON file
    log_event(identifier, vibe, meme_text)
    
    image = Image.open(BytesIO(image_bytes)).convert("RGB") #load uploaded image
    draw = ImageDraw.Draw(image) #create a drawing context
  
    # Load Impact font
    font_path = "fonts/impact.ttf"
    
    # Adjust font size based on image width
    if image.width < 1000:
        font_size = int(image.height * 0.05)  # 5% for smaller images
    else:
        font_size = int(image.height * 0.07)  # 7% for larger images

    font = ImageFont.truetype(font_path, font_size)
    # papyrus = ImageFont.truetype("fonts/Papyrus.ttf", font_size)  # Load Papyrus font for watermark
    # ADD WATERMARK LOGIC HERE
    # Watermark settings
    watermark_text = "Meme Aunty by Archit80"
    watermark_font_size = max(16, int(image.height * 0.0375))  # Minimum 16px, scales with image (increased from 0.015 to 0.025)
    
    try:
        # Use the calculated font size with Impact font
        watermark_font = ImageFont.truetype(font_path, watermark_font_size)
    except:
        # Fallback to default font
        watermark_font = ImageFont.load_default()
    
    # Calculate watermark position (top right)
    watermark_bbox = draw.textbbox((0, 0), watermark_text, font=watermark_font)
    watermark_width = watermark_bbox[2] - watermark_bbox[0]
    watermark_height = watermark_bbox[3] - watermark_bbox[1]
    
    watermark_x = image.width - watermark_width - 15  # 15px margin from right
    watermark_y = 15  # 15px margin from top
    
    # Draw watermark without outline
    def draw_watermark_with_outline(draw, x, y, text, font):
        # Simple watermark text without outline
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 200))  # Semi-transparent white
    
    # Draw the watermark
    draw_watermark_with_outline(draw, watermark_x, watermark_y, watermark_text, watermark_font)
    
    bbox = draw.textbbox((0, 0), meme_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    image_width, image_height = image.size #calculate image size

    x = (image_width - text_width) // 2  #x position to center the text
    y = image_height - text_height - 20  #y position of text at bottom with margin 20

    def wrap_text(text, font, max_width):
        lines = []
        words = text.split()
        line = ""
        for word in words:
            test_line = f"{line} {word}".strip()
            if draw.textlength(test_line, font=font) <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word
        lines.append(line)
        return lines

    wrapped_lines = wrap_text(meme_text, font, image.width - 40)

    # Text drawing with outline
    def draw_text_with_outline(draw, x, y, text, font):
        # Adjust outline thickness based on image size
        if image.width < 1000 or image.height < 1000:
            outline_range = [-1, 0, 1]  # Thinner outline for smaller images
        else:
            outline_range = [-2, -1, 0, 1, 2]  # Thicker outline for larger images
            
        for dx in outline_range:
            for dy in outline_range:
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill="black")
        draw.text((x, y), text, font=font, fill="white")

    # Draw each line
    line_height = font.getbbox("A")[3] + 10  # Height + spacing
    total_text_height = line_height * len(wrapped_lines)
    current_y =  image.height - total_text_height - 20  # from bottom with margin 20
    
    for line in wrapped_lines:
        text_width = draw.textlength(line, font=font)
        x = (image.width - text_width) // 2
        draw_text_with_outline(draw, x, current_y, line, font)
        current_y += line_height

    # Save to memory
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)

    # Upload to Cloudinary
    upload_result = cloudinary.uploader.upload(buffer, folder="memes", resource_type="image")
    meme_url = upload_result["secure_url"]


    return JSONResponse(content={
        "meme_url": meme_url,
        "caption": meme_text
    })


# Run the FastAPI app using uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

