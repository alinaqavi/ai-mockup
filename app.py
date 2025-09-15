from flask import Flask, request, jsonify
from openai import OpenAI
import os
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

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

        if not product_file or not logo_file:
            return jsonify({"error": "Product image and logo are required"}), 400

        # ✅ Save files temporarily
        product_path = f"temp_product_{product_file.filename}"
        logo_path = f"temp_logo_{logo_file.filename}"
        product_file.save(product_path)
        logo_file.save(logo_path)

        prompt = "Place the uploaded logo on the product realistically."

        # ✅ Open files and pass to OpenAI
        with open(product_path, "rb") as p_img, open(logo_path, "rb") as l_img:
            response = client.images.edit(
                model="gpt-image-1",
                image=p_img,
                prompt=prompt,
                mask=l_img,
                size="1024x1024"
            )

        # ✅ Remove temp files
        os.remove(product_path)
        os.remove(logo_path)

        return jsonify({
            "variant": variant,
            "image_url": response.data[0].url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
