import streamlit as st
import google.generativeai as genai
import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from google.colab import userdata # Only for Colab to fetch API key from secrets

st.set_page_config(layout="wide")

st.title("AI Meme & Poster Creator")
st.write("Generate creative memes and posters with AI-powered captions!")

# Initialize the Generative Model within app.py
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        api_key = userdata.get('GOOGLE_API_KEY', None)

    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
    else:
        st.error("Google API Key not found. Please set 'GOOGLE_API_KEY' in Colab secrets or environment variables.")
        model = None
except Exception as e:
    st.error(f"Error configuring Gemini API: {e}")
    model = None


def generate_caption(prompt_text, current_model):
    if current_model is None:
        return "AI model not configured. Cannot generate caption."
    try:
        response = current_model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        return f"Error generating caption: {e}. Check your API key and model access."

# Function to create a meme/poster image
def create_meme(image, caption_text):
    img = Image.open(image).convert("RGBA")
    img_width, img_height = img.size

    # Make image editable
    draw = ImageDraw.Draw(img)

    # Define font (you might need to adjust path/name depending on environment)
    try:
        font = ImageFont.truetype("arial.ttf", 36) # Common font, adjust size
    except IOError:
        font = ImageFont.load_default() # Fallback to default if arial.ttf is not found

    # Calculate text size and position
    text_width, text_height = draw.textsize(caption_text, font)
    x = (img_width - text_width) / 2
    y = img_height - text_height - 10 # Position at bottom, with some padding

    # Add white rectangle behind text for better readability (optional)
    draw.rectangle(((x-5, y-5), (x + text_width + 5, y + text_height + 5)), fill="white")

    # Add text to image
    draw.text((x, y), caption_text, font=font, fill="black") # Black text on white background

    # Convert back to RGB for Streamlit display
    img = img.convert("RGB")

    return img

st.subheader("1. Enter Your Caption Idea")
caption_input = st.text_area("Start typing your caption or idea here:", "A funny caption for a meme...")

st.subheader("2. Upload Your Image")
uploaded_file = st.file_uploader("Choose an image file (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

if st.button("Generate Meme/Poster"):
    if not caption_input:
        st.warning("Please enter some text for the caption.")
    if uploaded_file is None:
        st.warning("Please upload an image.")

    if caption_input and uploaded_file is not None:
        with st.spinner("Generating caption and image..."):
            # Generate caption
            generated_text = generate_caption(caption_input, model)
            st.subheader("Generated Caption")
            st.write(generated_text)

            # Create meme with image and generated caption
            try:
                meme_image = create_meme(uploaded_file, generated_text)
                st.subheader("Generated Meme/Poster")
                st.image(meme_image, caption="Your AI-generated creation!", use_column_width=True)
            except Exception as e:
                st.error(f"Error creating meme: {e}")

st.subheader("Preview of Uploaded Image")
if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
else:
    st.info("Upload an image to see a preview here.")

