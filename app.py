from flask import Flask, request, jsonify
from openai import OpenAI
import os
from flask_cors import CORS
from dotenv import load_dotenv
from PIL import Image
import io

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
def resize_image(file, max_size=800):
    img = Image.open(file)
    img.thumbnail((max_size, max_size))
    return img

# ✅ Overlay helper
def overlay_logo(product_img, logo_img, position=(50, 50)):
    if logo_img.mode != 'RGBA':
        logo_img = logo_img.convert("RGBA")
    product_img.paste(logo_img, position, logo_img)
    return product_img

@app.route("/generate-mockup", methods=["POST"])
def generate_mockup():
    try:
        product_file = request.files.get("product")
        logo_file = request.files.get("logo")
        variant = request.form.get("variant", "default")

        if not product_file:
            return jsonify({"error": "Product image required"}), 400

        # ✅ Resize product and logo for memory efficiency
        product_img = resize_image(product_file)
        logo_img = resize_image(logo_file) if logo_file else None

        # ✅ Overlay logo if provided
        if logo_img:
            product_img = overlay_logo(product_img, logo_img)

        # ✅ Convert image to bytes for OpenAI
        img_bytes = io.BytesIO()
        product_img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        prompt = "Make the product look like a professional mockup with logo applied." if logo_file else \
                 "Make the product look like a professional mockup."

        # ✅ Send request to OpenAI
        response = client.images.edit(
            model="gpt-image-1",
            image=("product.png", img_bytes, "image/png"),
            prompt=prompt,
            size="1024x1024"
        )

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
