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


@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/explore")
def explore():
    user_id = session.get("user_id")
    

    tab = request.args.get("tab","part-time")
    
    jobs = supabase.table("jobs").select("*")
    if tab == "part-time":
        jobs = jobs.eq("type","part-time").execute().data
    elif tab == "specialised":
        jobs = jobs.eq("type","specialised").execute().data
    elif tab == "favourites":
        if not user_id:
            return render_template("explore.html", jobs = None, tab = tab)
        else:
            favourites = supabase.table("favourites").select("job_id").eq("user_id",user_id).execute().data
            fav_ids = [f["job_id"] for f in favourites]
            if not fav_ids:
                jobs = None
            jobs = jobs.in_("id",fav_ids)
    return render_template("explore.html", jobs = jobs, tab = tab)

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
        return redirect(url_for("signIn"))

    age = request.form.get("age")
    language = request.form.getlist("language[]")
    location = request.form.getlist("location[]")
    education = request.form.get("education")
    needs = request.form.get("needs")
    internet = request.form.get("internet")
    physical = request.form.get("physical")
    preference = request.form.get("preference")
    digital = request.form.getlist("digital[]")
    service = request.form.getlist("service[]")
    technical = request.form.getlist("technical[]")
    logistics = request.form.getlist("logistics[]")
    experience = request.form.getlist("experience[]")
    skills = digital + service + technical + logistics + experience
    job_list = supabase.table("jobs").select("*").eq("age",age).overlaps("languages",language).overlaps("education",education)
    if physical =="no":
        job_list = job_list.eq("physical",physical)
    if internet == "no":
        job_list = job_list.eq("internet",internet)
    
    
    if needs=="income":
        job_list = job_list.eq("needs",needs).eq("income_type","fixed")
    job_list = job_list.order("salary", desc=True).execute().data
    if needs=="income":
        filtered_jobs = []
        for job in job_list:
            requirements = job["requirements"]
            if all(req in skills for req in requirements):
                filtered_jobs.append(job)
        job_list = filtered_jobs
    ranked_jobs = []
    for job in job_list:
        category = job["category"]
    supabase.table("profile").upsert({
       "age": age,
       "languages": language,
       "education":education,
       "location":location,
       "needs": needs,
       "internet": internet,
       "physical": physical,
       "preference": preference,
       "digital": digital,
       "service": service,
       "technical": technical,
       "logistics": logistics,
       "experience": experience,
       "user_id": session.get("user_id")
   }).execute()
    return render_template("quiz_results.html", needs = needs, job_list = job_list)


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

#flask --app app run --debug --port 5001
    
