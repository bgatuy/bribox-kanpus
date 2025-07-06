from flask import Flask, request, jsonify
from extract_report import extract_pdf
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({"error": "No PDF uploaded"}), 400
    file = request.files['pdf']
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)
    result = extract_pdf(path)
    return jsonify({"text": result})

if __name__ == "__main__":
    app.run(debug=True)
