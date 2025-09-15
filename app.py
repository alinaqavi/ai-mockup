from flask import Flask, request, jsonify
from openai import OpenAI
import os
from flask_cors import CORS
from dotenv import load_dotenv
from io import BytesIO

# ✅ Load env
load_dotenv()

app = Flask(__name__)
CORS(app)

# ✅ OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET"])
def home():
    return "🚀 AI Mockup Backend is running. Use POST /generate-mockup"

@app.route("/generate-mockup", methods=["POST"])
def generate_mockup():
    try:
        # ✅ Files
        product_file = request.files.get("product")
        logo_file = request.files.get("logo")  # optional
        variant = request.form.get("variant", "default")

        if not product_file:
            return jsonify({"error": "Product image required"}), 400

        # ✅ Prompt banado
        if logo_file:
            prompt = "Place the uploaded logo on the product realistically."
        else:
            prompt = "Make the product photo look like a professional mockup."

        # ✅ OpenAI call (NO MASK)
        response = client.images.edit(
            model="gpt-image-1",
            image=BytesIO(product_file.read()),
            prompt=prompt,
            size="1024x1024"
        )

        # ✅ Image URL extract
        image_url = response.data[0].url if response.data else None

        return jsonify({
            "variant": variant,
            "image_url": image_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
