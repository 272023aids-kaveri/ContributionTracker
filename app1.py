from flask import Flask, render_template
from flask import request, redirect
from flask import session, make_response

from report_generator import generate_pdf

import os
import io
from docx import Document
import PyPDF2

# Absolute path for PDF to avoid stale file issues
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

app = Flask(__name__)

app.secret_key = "secret123"

if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

# =====================================================
# IMPORTANT: Exclude uploads folder from watchdog
# so uploading .py files doesn't restart the server
# =====================================================

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# =====================================================
# FILE ANALYZER
# =====================================================

def analyze_file(filepath):

    score = 0

    ext = os.path.splitext(filepath)[1].lower()

    try:

        # ---------------- CODE FILES ----------------

        if ext in [".py", ".java", ".js", ".html", ".css"]:

            with open(filepath, "r", encoding="utf-8") as f:

                content = f.read()

            lines = len(content.splitlines())

            words = len(content.split())

            functions = content.count("def ")

            score = (
                lines * 0.5
                + words * 0.1
                + functions * 5
            )

        # ---------------- TEXT FILE ----------------

        elif ext == ".txt":

            with open(filepath, "r", encoding="utf-8") as f:

                content = f.read()

            words = len(content.split())

            score = words * 0.5

        # ---------------- DOCX FILE ----------------

        elif ext == ".docx":

            doc = Document(filepath)

            text = ""

            for para in doc.paragraphs:

                text += para.text

            words = len(text.split())

            score = words * 0.7

        # ---------------- PDF FILE ----------------

        elif ext == ".pdf":

            with open(filepath, "rb") as f:

                reader = PyPDF2.PdfReader(f)

                text = ""

                for page in reader.pages:

                    extracted = page.extract_text()

                    if extracted:

                        text += extracted

            words = len(text.split())

            score = words * 0.8

        # ---------------- OTHER FILES ----------------

        else:

            size = os.path.getsize(filepath)

            score = size / 1000

    except:

        score = 10

    return round(score)

# =====================================================
# LOGIN PAGE
# =====================================================

@app.route("/")
def login():

    return render_template("login.html")

# =====================================================
# LOGIN CHECK
# =====================================================

@app.route("/login", methods=["POST"])
def do_login():

    username = request.form["username"]

    password = request.form["password"]

    if username == "Prachi" and password == "345":

        session.clear()  # Clear old session data on fresh login

        return redirect("/members")

    return render_template(
        "login.html",
        error=True
    )

# =====================================================
# ADD MEMBERS
# =====================================================

@app.route("/members", methods=["GET", "POST"])
def add_members():

    if request.method == "POST":

        # Clear any old session data before saving new members
        session.clear()

        # COLLEGE NAME

        college_name = request.form.get("college_name", "")

        # DEPARTMENT NAME

        department = request.form.get("department", "")

        # GUIDE NAME

        guide = request.form.get("guide", "")

        # PROJECT TITLE

        project_title = request.form.get(
            "project_title",
            ""
        )

        members = []

        contributions = {}

        member_count = int(
            request.form.get("memberCount", 0)
        )

        for i in range(1, member_count + 1):

            member_name = request.form.get(
                f"member{i}",
                ""
            )

            prn = request.form.get(
                f"prn{i}",
                ""
            )

            role = request.form.get(
                f"role{i}",
                ""
            )

            if member_name != "":

                member_data = {

                    "name": member_name,
                    "prn": prn,
                    "role": role

                }

                members.append(member_data)

                contributions[member_name] = 0

        # SAVE SESSION

        session["college_name"] = college_name

        session["department"] = department

        session["guide"] = guide

        session["project_title"] = project_title

        session["members"] = members

        session["contributions"] = contributions

        return redirect("/dashboard")

    return render_template("member.html")

# =====================================================
# DASHBOARD
# =====================================================

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    members = session.get("members", [])

    contributions = session.get(
        "contributions",
        {}
    )

    project_title = session.get(
        "project_title",
        ""
    )

    message = ""

    if request.method == "POST":

        uploader = request.form["uploader"]

        file = request.files["file"]

        if file:

            filepath = os.path.join(
                UPLOAD_FOLDER,
                file.filename
            )

            file.save(filepath)

            # ANALYZE FILE

            score = analyze_file(filepath)

            # ADD SCORE

            if uploader not in contributions:

                contributions[uploader] = 0

            contributions[uploader] += score

            session["contributions"] = contributions

            message = (
                f"{uploader} uploaded successfully! "
                f"Contribution Score Added: {score}"
            )

    # =====================================================
    # CALCULATE PERCENTAGES
    # =====================================================

    total = sum(contributions.values())

    percentages = {}

    for member in members:

        member_name = member["name"]

        if total == 0:

            percentages[member_name] = 0

        else:

            percentages[member_name] = round(
                (contributions[member_name] / total) * 100
            )

    return render_template(
        "index.html",
        members=members,
        contributions=contributions,
        percentages=percentages,
        message=message,
        project_title=project_title
    )

# =====================================================
# REPORT PAGE
# =====================================================

@app.route("/report")
def report():

    college_name = session.get("college_name", "")

    department = session.get("department", "")

    guide = session.get("guide", "")

    project_title = session.get(
        "project_title",
        ""
    )

    members = session.get("members", [])

    contributions = session.get(
        "contributions",
        {}
    )

    total = sum(contributions.values())

    percentages = {}

    for member in members:

        member_name = member["name"]

        if total == 0:

            percentages[member_name] = 0

        else:

            percentages[member_name] = round(
                (contributions[member_name] / total) * 100
            )

    return render_template(
        "report.html",
        college_name=college_name,
        department=department,
        guide=guide,
        project_title=project_title,
        members=members,
        contributions=contributions,
        percentages=percentages,
        total=total
    )

# =====================================================
# SCORE PAGE
# =====================================================

@app.route("/score")
def score():

    guide = session.get("guide", "")

    project_title = session.get(
        "project_title",
        ""
    )

    members = session.get("members", [])

    contributions = session.get(
        "contributions",
        {}
    )

    total = sum(contributions.values())

    percentages = {}

    for member in members:

        member_name = member["name"]

        if total == 0:

            percentages[member_name] = 0

        else:

            percentages[member_name] = round(
                (contributions[member_name] / total) * 100
            )

    return render_template(
        "score.html",
        guide=guide,
        project_title=project_title,
        members=members,
        contributions=contributions,
        percentages=percentages,
        total=total
    )

# =====================================================
# DOWNLOAD PDF
# =====================================================

@app.route("/download_pdf")
def download_pdf():

    # GET DATA FROM SESSION

    college_name = session.get(
        "college_name",
        ""
    )

    department = session.get(
        "department",
        ""
    )

    project_title = session.get(
        "project_title",
        ""
    )

    guide = session.get(
        "guide",
        ""
    )

    members = session.get(
        "members",
        []
    )

    contributions = session.get(
        "contributions",
        {}
    )

    # CALCULATE TOTAL

    total = sum(
        contributions.values()
    )

    # CALCULATE PERCENTAGES

    percentages = {}

    for member in members:

        name = member["name"]

        score = contributions.get(name, 0)

        if total == 0:

            percentages[name] = 0

        else:

            percentages[name] = round(
                (score / total) * 100
            )

    # GENERATE PDF INTO MEMORY BUFFER

    pdf_buffer = io.BytesIO()

    generate_pdf(
        project_title,
        guide,
        members,
        contributions,
        percentages,
        total,
        pdf_buffer,
        college_name,
        department
    )

    pdf_buffer.seek(0)

    # BUILD RESPONSE WITH EXPLICIT HEADERS

    response = make_response(pdf_buffer.read())

    response.headers['Content-Type'] = 'application/pdf'

    response.headers['Content-Disposition'] = (
        'attachment; filename=AI_Contribution_Report.pdf'
    )

    return response

# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# =====================================================
# RUN APP
# =====================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"

    app.run(host=host, port=port, debug=debug)
