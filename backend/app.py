from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, create_access_token
import openai
from deep_translator import GoogleTranslator

app = Flask(__name__)
app.config.from_object("config.Config")
CORS(app)

mongo = PyMongo(app)
jwt = JWTManager(app)

openai.api_key = "your_openai_api_key"

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    if mongo.db.users.find_one({"email": data["email"]}):
        return jsonify({"message": "User already exists"}), 400
    mongo.db.users.insert_one(data)
    return jsonify({"message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = mongo.db.users.find_one({"email": data["email"]})
    if not user or user["password"] != data["password"]:
        return jsonify({"message": "Invalid credentials"}), 401
    token = create_access_token(identity=data["email"])
    return jsonify({"token": token})

@app.route("/summarize", methods=["POST"])
def summarize():
    text = request.json.get("text", "")
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Summarize this: {text}",
        max_tokens=50
    )
    return jsonify({"summary": response.choices[0].text.strip()})

@app.route("/translate", methods=["POST"])
def translate():
    data = request.json
    translated_text = GoogleTranslator(source="auto", target=data["lang"]).translate(data["text"])
    return jsonify({"translated_text": translated_text})

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Flask Backend is Running!"})


if __name__ == "__main__":
    app.run(debug=True)
