from flask import Flask, request, jsonify
from openai import OpenAI
import os
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET"])
def home():
    return "🚀 AI Mockup Backend is running. Use POST /generate-mockup"

@app.route("/generate-mockup", methods=["POST"])
def generate_mockup():
    try:
        # Get uploaded files
        product_file = request.files.get("product")
        logo_file = request.files.get("logo")
        variant = request.form.get("variant", "default")

        if not product_file or not logo_file:
            return jsonify({"error": "Product image and logo are required"}), 400

        # Save files temporarily
        product_path = f"temp_product_{product_file.filename}"
        logo_path = f"temp_logo_{logo_file.filename}"
        product_file.save(product_path)
        logo_file.save(logo_path)

        # Prompt for AI
        prompt = "Place the uploaded logo on this product realistically."

        # Use images.generate instead of images.edit
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            n=1
        )

        # Remove temporary files
        os.remove(product_path)
        os.remove(logo_path)

        image_url = response.data[0].url

        return jsonify({
            "variant": variant,
            "image_url": image_url
        })

    except Exception as e:
        print("Error:", e)  # Terminal me actual error
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
