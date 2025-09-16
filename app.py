from flask import Flask, request, jsonify
from openai import OpenAI
import os
from flask_cors import CORS
from dotenv import load_dotenv
from PIL import Image
import uuid

# ✅ Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# ✅ OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET"])
def home():
    return "🚀 AI Mockup Backend is running. Use POST /generate-mockup"

# ✅ Resize helper
def resize_image(file_path, max_size=800):
    img = Image.open(file_path)
    img.thumbnail((max_size, max_size))
    img.save(file_path)  # overwrite resized image
    return file_path

# ✅ Overlay helper
def overlay_logo(product_path, logo_path, position=(50, 50)):
    product_img = Image.open(product_path).convert("RGBA")
    logo_img = Image.open(logo_path).convert("RGBA")
    product_img.paste(logo_img, position, logo_img)
    # Save overlayed image to same path
    product_img.save(product_path)
    return product_path

@app.route("/generate-mockup", methods=["POST"])
def generate_mockup():
    try:
        product_file = request.files.get("product")
        logo_file = request.files.get("logo")
        variant = request.form.get("variant", "default")

        if not product_file:
            return jsonify({"error": "Product image required"}), 400

        # ✅ Generate temp file paths
        product_path = f"temp_{uuid.uuid4().hex}.png"
        product_file.save(product_path)

        # Resize product
        resize_image(product_path)

        # Overlay logo if provided
        if logo_file:
            logo_path = f"temp_{uuid.uuid4().hex}_logo.png"
            logo_file.save(logo_path)
            resize_image(logo_path)
            overlay_logo(product_path, logo_path)

        # ✅ Send to OpenAI edit API
        with open(product_path, "rb") as f:
            prompt = "Make the product look like a professional mockup with logo applied." if logo_file else \
                     "Make the product look like a professional mockup."
            response = client.images.edit(
                model="gpt-image-1",
                image=(product_path, f, "image/png"),
                prompt=prompt,
                size="1024x1024"
            )

        # Clean up temp files
        os.remove(product_path)
        if logo_file:
            os.remove(logo_path)

        image_url = response.data[0].url if response and response.data else None

        return jsonify({
            "variant": variant,
            "image_url": image_url
        })

    except Exception as e:
        return jsonify({"error": f"Error code: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
