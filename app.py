from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
"""
def handle_message(msg):
    return f"u said {msg}"

@app.route("/chat",methods = ["POST"])
def chat():
    msg = request.json["message"]
    reply = handle_message(msg)
    return jsonify({"reply": reply})
"""

@app.route("/")
def signIn():
    return render_template("signIn.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/jobGuide")
def jobGuide():
    return render_template("jobGuide.html")

@app.route("/donate")
def donate():
    return render_template("donate.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)

#flask --app app run --debug