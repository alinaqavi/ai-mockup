from flask import Flask, request, jsonify
import openai
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend requests

# ✅ API Key environment variable se lo
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ Root route (testing)
@app.route("/", methods=["GET"])
def home():
    return "🚀 AI Mockup Backend is running. Use POST /generate-mockup"

# ✅ Mockup generate route
@app.route("/generate-mockup", methods=["POST"])
def generate_mockup():
    try:
        # Frontend se inputs
        product = request.form.get("product")
        variant = request.form.get("variant")
        logo_file = request.files.get("logo")

        if not product or not logo_file:
            return jsonify({"error": "Product and logo are required"}), 400

        # ✅ Prompt banate hain
        prompt = f"Create a 3D realistic mockup of a {product} ({variant}) with the uploaded logo placed on it. High quality studio render."

        # ✅ Call OpenAI Image API
        response = openai.images.generate(
            model="gpt-image-1",   # DALL·E 3
            prompt=prompt,
            size="1024x1024"
        )

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
