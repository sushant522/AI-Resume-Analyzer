import pdfplumber
import pandas as pd
import re

#?????????????????????????

def pdf_reader(file):
    text = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text

##/////////////

def extract_resume_data(resume_text, pdf_path):
    data = {}

    # -------------------------
    # Name Extraction
    # -------------------------
    lines = [line.strip() for line in resume_text.split("\n") if line.strip()]

    ignored_words = {
        "resume",
        "curriculum vitae",
        "cv",
        "profile",
        "summary",
        "objective",
        "education",
        "experience",
        "skills",
        "projects",
        "contact",
    }

    name = ""
    for line in lines[:10]:  # Check only the first few lines
        lower_line = line.lower()

        if (
            lower_line not in ignored_words
            and "@" not in line
            and not any(char.isdigit() for char in line)
            and 2 <= len(line.split()) <= 4
        ):
            name = line
            break

    data["name"] = name

    # -------------------------
    # Email Extraction
    # -------------------------
    email_pattern = r"[\w\.-]+@[\w\.-]+\.\w+"
    emails = re.findall(email_pattern, resume_text)
    data["email"] = emails[0] if emails else ""

    # -------------------------
    # Phone Number Extraction
    # -------------------------
    phone_pattern = r"(?:\+91[\-\s]?)?[6-9]\d{9}"
    phones = re.findall(phone_pattern, resume_text)

    data["mobile_number"] = phones[0] if phones else ""

    # -------------------------
    # Number of Pages
    # -------------------------
    try:
        with pdfplumber.open(pdf_path) as pdf:
            data["no_of_pages"] = len(pdf.pages)
    except Exception:
        data["no_of_pages"] = 0

    # -------------------------
    # Skills Extraction
    # -------------------------
    try:
        skills_df = pd.read_csv("skills.csv")

        skills_df["skill"] = skills_df["skill"].astype(str)

        text_lower = resume_text.lower()
        found_skills = []

        for skill in skills_df["skill"]:
            pattern = rf"\b{re.escape(skill.lower())}\b"

            if re.search(pattern, text_lower):
                found_skills.append(skill)

        # Remove duplicates while preserving order
        found_skills = list(dict.fromkeys(found_skills))

        data["skills"] = found_skills

        # -------------------------
        # Predicted Field
        # -------------------------
        matched_rows = skills_df[
            skills_df["skill"].isin(found_skills)
        ]

        if not matched_rows.empty:
            data["predicted_field"] = (
                matched_rows["category"].mode().iloc[0]
            )
        else:
            data["predicted_field"] = "Unknown"

    except Exception as e:
        print(f"Skill extraction error: {e}")
        data["skills"] = []
        data["predicted_field"] = "Unknown"

    return data
