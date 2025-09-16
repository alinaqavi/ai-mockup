from flask import Flask, request, jsonify
from openai import OpenAI
import os
from flask_cors import CORS
from dotenv import load_dotenv

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
        product_file = request.files.get("product")
        logo_file = request.files.get("logo")
        variant = request.form.get("variant", "default")

        if not product_file:
            return jsonify({"error": "Product image required"}), 400

        # ✅ Fix mimetype if missing/wrong
        def fix_mime(file):
            mimetype = file.mimetype
            if mimetype == "application/octet-stream":
                if file.filename.lower().endswith((".jpg", ".jpeg")):
                    mimetype = "image/jpeg"
                elif file.filename.lower().endswith(".png"):
                    mimetype = "image/png"
                elif file.filename.lower().endswith(".webp"):
                    mimetype = "image/webp"
            return mimetype

        product_mime = fix_mime(product_file)

        prompt = "Place the uploaded logo on the product realistically." if logo_file else \
                 "Make the product photo look like a professional mockup."

        # ✅ Send request to OpenAI
        response = client.images.edit(
            model="gpt-image-1",
            image=(product_file.filename, product_file, product_mime),
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
