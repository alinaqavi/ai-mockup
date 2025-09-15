from flask import Flask, request, jsonify
from openai import OpenAI
import os
from flask_cors import CORS
from dotenv import load_dotenv
import base64

# ✅ Load environment variables for local testing
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
        product = request.form.get("product")
        variant = request.form.get("variant")
        logo_file = request.files.get("logo")  # Required file

        if not product or not logo_file:
            return jsonify({"error": "Product and logo are required"}), 400

        # ✅ Save uploaded logo temporarily
        logo_path = f"temp_logo_{logo_file.filename}"
        logo_file.save(logo_path)

        # ✅ Prepare prompt
        prompt = f"Create a 3D realistic mockup of a {product} ({variant}) with the uploaded logo placed on it. High quality studio render."

        # ✅ Call OpenAI Image API with logo as input
        with open(logo_path, "rb") as f:
            response = client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size="1024x1024",
                image=f
            )

        # ✅ Image URL or base64 extract
        image_url = response.data[0].url  # Or response.data[0].b64_json for base64

        # ✅ Optional: delete temp logo file
        os.remove(logo_path)

        return jsonify({
            "product": product,
            "variant": variant,
            "image_url": image_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
