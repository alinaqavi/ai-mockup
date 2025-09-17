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
    img.save(file_path)
    return file_path

# ✅ Overlay helper
def overlay_logo(product_path, logo_path, position=(50, 50)):
    product_img = Image.open(product_path).convert("RGBA")
    logo_img = Image.open(logo_path).convert("RGBA")
    product_img.paste(logo_img, position, logo_img)
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

        # ✅ Temp file paths
        product_path = f"temp_{uuid.uuid4().hex}.png"
        product_file.save(product_path)
        resize_image(product_path)

        # ✅ Overlay logo locally if provided
        if logo_file:
            logo_path = f"temp_{uuid.uuid4().hex}_logo.png"
            logo_file.save(logo_path)
            resize_image(logo_path)
            overlay_logo(product_path, logo_path)
            os.remove(logo_path)

        # ❌ OpenAI function call OFF
        """
        prompt = "Create a professional product mockup based on this image."
        with open(product_path, "rb") as f:
            response = client.images.generate(
                model="dall-e-3-standard",  # ✅ Standard pricing 0.04$/image
                prompt=prompt,
                image=f,  # optional base image for variation
                size="1024x1024",
                n=1
            )
        """

        # ✅ Fallback: return local file path
        image_url = f"/{product_path}"

        return jsonify({
            "variant": variant,
            "image_url": image_url
        })

    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
