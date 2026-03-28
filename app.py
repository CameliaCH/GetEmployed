from flask import Flask, request, jsonify, render_template, session, flash, url_for, redirect
from passlib.hash import argon2
from dotenv import load_dotenv
from db import supabase
import os

load_dotenv()
app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "dev-secret")
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

from blueprints.interview import interview_bp
app.register_blueprint(interview_bp, url_prefix='/interview')

@app.route("/interview")
def interview():
    return render_template("interview.html")
@app.route("/")
def home():
    return render_template("home.html")
@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/your-applications")
def applications():
    return render_template("your-applications.html")


@app.route("/explore")
def explore():
    user_id = session.get("user_id")
    tab = request.args.get("tab", "part-time")

    jobs_query = supabase.table("jobs").select("*")

    if tab == "part-time":
        jobs = jobs_query.eq("type", "part-time").execute().data
    elif tab == "specialised":
        jobs = jobs_query.eq("type", "specialised").execute().data
    elif tab == "favourites":
        if not user_id:
            return render_template("explore.html", jobs=None, tab=tab)
        favourites = supabase.table("favourites").select("job_id").eq("user_id", user_id).execute().data
        fav_ids = [f["job_id"] for f in favourites]
        if not fav_ids:
            jobs = []
        else:
            jobs = jobs_query.in_("id", fav_ids).execute().data
    else:
        jobs = jobs_query.execute().data

    return render_template("explore.html", jobs=jobs, tab=tab)


@app.route("/jobs")
def jobs():
    return render_template("jobs.html")


@app.route("/job")
def job():
    return render_template("job.html")


@app.route("/quiz")
def quiz():
    return render_template("quiz.html")


@app.route("/quiz_results", methods=["POST"])
def quiz_results():
    if "user_id" not in session:
        flash("Please sign in to see your personalised roadmap.", "warning")
        return redirect(url_for("signIn"))

    age        = request.form.get("age")
    language   = request.form.getlist("language[]")
    location   = request.form.getlist("location[]")
    education  = request.form.get("education")
    needs      = request.form.get("needs")
    internet   = request.form.get("internet")
    physical   = request.form.get("physical")
    preference = request.form.get("preference")
    digital    = request.form.getlist("digital[]")
    service    = request.form.getlist("service[]")
    technical  = request.form.getlist("technical[]")
    logistics  = request.form.getlist("logistics[]")
    experience = request.form.getlist("experience[]")
    skills     = digital + service + technical + logistics + experience

    job_query = supabase.table("jobs").select("*").eq("age", age)

    if language:
        job_query = job_query.overlaps("languages", language)
    if education:
        job_query = job_query.overlaps("education", [education])
    if physical == "no":
        job_query = job_query.eq("physical", "no")
    if internet == "no":
        job_query = job_query.eq("internet", "no")
    if needs == "income":
        job_query = job_query.eq("needs", "income").eq("income_type", "fixed")

    job_list = job_query.order("salary", desc=True).execute().data

    # Filter by matching skill requirements (only for immediate-income path)
    if needs == "income":
        job_list = [
            job for job in job_list
            if all(req in skills for req in (job.get("requirements") or []))
        ]

    # Save profile answers
    supabase.table("profile").upsert({
        "user_id":    session.get("user_id"),
        "age":        age,
        "languages":  language,
        "education":  education,
        "location":   location,
        "needs":      needs,
        "internet":   internet,
        "physical":   physical,
        "preference": preference,
        "digital":    digital,
        "service":    service,
        "technical":  technical,
        "logistics":  logistics,
        "experience": experience,
    }).execute()

    return render_template("quiz_results.html", needs=needs, job_list=job_list)


@app.route("/know")
def know():
    return render_template("know.html")


@app.route("/skills")
def skills():
    return render_template("skills.html")


@app.route("/CVexamples")
def CVexamples():
    return render_template("CVexamples.html")


@app.route("/jobGuide")
def jobGuide():
    return render_template("jobGuide.html")


@app.route("/donate")
def donate():
    return render_template("donate.html")


@app.route("/signIn", methods=["GET", "POST"])
def signIn():
    if request.method == "POST":
        name     = request.form.get("name")
        email    = request.form.get("email")
        password = request.form.get("password")

        existing = supabase.table("users").select("*").eq("email", email).execute().data

        if existing:
            user = existing[0]
            if not argon2.verify(password, user["password_hash"]):
                flash("Incorrect password. Please try again.", "error")
                return redirect(url_for("signIn"))

            # ✅ BUG FIX: store user_id in session (was missing before)
            session["user_id"]    = user["id"]
            session["user_email"] = user["email"]
            session["user_name"]  = user["name"]
            flash("Welcome back, {}!".format(user["name"]), "success")
            return redirect(url_for("home"))

        # New user registration
        pw_hash = argon2.hash(password)
        result  = supabase.table("users").insert({
            "email":         email,
            "name":          name,
            "password_hash": pw_hash,
        }).execute()

        new_user = result.data[0] if result.data else {}
        session["user_id"]    = new_user.get("id")
        session["user_email"] = email
        session["user_name"]  = name
        flash("Account created! Welcome, {}.".format(name), "success")
        return redirect(url_for("home"))

    return render_template("signIn.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)

# flask --app app run --debug --port 5001
