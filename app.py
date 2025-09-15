from flask import Flask, request, jsonify
from openai import OpenAI
import os
from flask_cors import CORS
from dotenv import load_dotenv

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
        # ✅ Get form data
        product = request.form.get("product")
        variant = request.form.get("variant", "default")
        logo_file = request.files.get("logo")

        if not product or not logo_file:
            return jsonify({"error": "Product and logo are required"}), 400

        # ✅ Save uploaded logo temporarily
        logo_path = f"temp_logo_{logo_file.filename}"
        logo_file.save(logo_path)

        # ✅ Define product image path (default image for each product)
        product_image_path = f"products/{product}_{variant}.png"
        if not os.path.exists(product_image_path):
            return jsonify({"error": f"Product image not found: {product_image_path}"}), 400

        # ✅ Prompt for placing the logo
        prompt = f"Place the uploaded logo on the {product} ({variant}) realistically."

        # ✅ Call OpenAI Images Edit API
        with open(product_image_path, "rb") as product_img, open(logo_path, "rb") as logo_img:
            response = client.images.edit(
                model="gpt-image-1",
                image=product_img,
                prompt=prompt,
                mask=logo_img,   # optional: controls logo placement
                size="1024x1024"
            )

        # ✅ Extract image URL
        image_url = response.data[0].url

        # ✅ Clean up temp logo
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
