from flask import Flask, request, jsonify
from openai import OpenAI
import os
from flask_cors import CORS
from dotenv import load_dotenv

# ✅ Load environment variables (local testing ke liye)
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow frontend requests

# ✅ Initialize OpenAI client with API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ Root route (for testing)
@app.route("/", methods=["GET"])
def home():
    return "🚀 AI Mockup Backend is running. Use POST /generate-mockup"

# ✅ Mockup generate route
@app.route("/generate-mockup", methods=["POST"])
def generate_mockup():
    try:
        # Frontend/Postman se inputs
        product = request.form.get("product")
        variant = request.form.get("variant")
        logo_file = request.files.get("logo")  # File required

        if not product or not logo_file:
            return jsonify({"error": "Product and logo are required"}), 400

        # ✅ Prompt banate hain
        prompt = f"Create a 3D realistic mockup of a {product} ({variant}) with the uploaded logo placed on it. High quality studio render."

        # ✅ Call OpenAI Image API (DALL·E via gpt-image-1)
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )

        # ✅ Image URL extract karo
        image_url = response.data[0].url

        return jsonify({
            "product": product,
            "variant": variant,
            "image_url": image_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
