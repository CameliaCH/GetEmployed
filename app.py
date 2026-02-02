from flask import Flask, request, jsonify, render_template, session, flash, url_for, redirect
from passlib.hash import argon2
from dotenv import load_dotenv
from db import supabase
import os

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

app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/careerQuiz")
def careerQuiz():
    return render_template("careerQuiz.html")

@app.route("/jobGuide")
def jobGuide():
    return render_template("jobGuide.html")

@app.route("/donate")
def donate():
    return render_template("donate.html")

@app.route("/", methods=["GET", "POST"])
def signIn():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        existing = supabase.table("users").select("*").eq("email",email).execute().data

        if existing:
            user = existing[0]
            if not argon2.verify(password, user["password_hash"]):
                flash("Incorrect password.")
                return redirect(url_for("signIn"))

            session["user_email"] = user["email"]
            session["user_name"] = user["name"]
            flash("Logged in!")
            return redirect(url_for("home"))

        pw_hash = argon2.hash(password)
        supabase.table("users").insert({
            "email": email,
            "name": name,
            "password_hash": pw_hash,
        }).execute()

        session["user_email"] = email
        session["user_name"] = name
        flash("Account created!")
        return redirect(url_for("home"))

    return render_template("signIn.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out!")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True, port=5001)

#flask --app app run --debug