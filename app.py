from flask import Flask, request, jsonify
import openai
import base64
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow Shopify frontend requests

# Set your OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY", "your_api_key_here")

@app.route("/generate-mockup", methods=["POST"])
def generate_mockup():
    try:
        product = request.form.get("product")
        variant = request.form.get("variant")
        logo_file = request.files.get("logo")

        if not logo_file:
            return jsonify({"error": "No logo uploaded"}), 400

        # Save uploaded logo temporarily
        logo_path = "logo.png"
        logo_file.save(logo_path)

        # Generate mockup image
        prompt = f"Create a realistic product mockup of a {product} ({variant}) with the uploaded company logo printed on it. High-quality studio lighting."

        response = openai.images.generate(
            model="gpt-image-1",   # DALL·E 3 API
            prompt=prompt,
            size="512x512"
        )

        image_url = response.data[0].url
        return jsonify({"image_url": image_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
