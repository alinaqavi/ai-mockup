from flask import Flask, request, jsonify
from openai import OpenAI
import os
from flask_cors import CORS
from dotenv import load_dotenv
from io import BytesIO
from werkzeug.datastructures import FileStorage  # ✅ Added

# ✅ Load environment variables from .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# ✅ Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET"])
def home():
    return "🚀 AI Mockup Backend is running. Use POST /generate-mockup"

@app.route("/generate-mockup", methods=["POST"])
def generate_mockup():
    try:
        # ✅ Get uploaded files
        product_file = request.files.get("product")
        logo_file = request.files.get("logo")
        variant = request.form.get("variant", "default")

        # ✅ Validate files
        if not product_file or not logo_file:
            return jsonify({"error": "Product image and logo are required"}), 400

        # ✅ Wrap uploaded files in FileStorage to preserve mimetype
        product_img = FileStorage(
            stream=BytesIO(product_file.read()),
            filename=product_file.filename,
            content_type=product_file.content_type  # important for OpenAI
        )

        logo_img = FileStorage(
            stream=BytesIO(logo_file.read()),
            filename=logo_file.filename,
            content_type=logo_file.content_type  # important for OpenAI
        )

        # ✅ Define prompt
        prompt = "Place the uploaded logo on the product realistically."

        # ✅ Call OpenAI Images Edit API
        response = client.images.edit(
            model="gpt-image-1",
            image=product_img,
            prompt=prompt,
            mask=logo_img,  # optional: controls logo placement
            size="1024x1024"
        )

        # ✅ Extract image URL
        image_url = response.data[0].url

        return jsonify({
            "variant": variant,
            "image_url": image_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
