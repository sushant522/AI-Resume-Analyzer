
"""
    Calculate Resume Quality Score (0-100)
"""
def calculate_resume_score(resume_text, resume_data, ats_score=None):

    score = 0
    suggestions = []

    resume_lower = resume_text.lower()

    # ---------------- Contact ----------------
    if resume_data.get("name"):
        score += 5
    else:
        suggestions.append("Add your full name.")

    if resume_data.get("email"):
        score += 5
    else:
        suggestions.append("Add your email address.")

    if resume_data.get("mobile_number"):
        score += 5
    else:
        suggestions.append("Add your phone number.")

    # ---------------- Education ----------------
    if "education" in resume_lower:
        score += 10
    else:
        suggestions.append("Add an Education section.")

    # ---------------- Skills ----------------
    skills = resume_data.get("skills", [])

    if len(skills) >= 10:
        score += 20
    elif len(skills) >= 7:
        score += 15
    elif len(skills) >= 4:
        score += 10
    else:
        score += 5
        suggestions.append("Add more relevant technical skills.")

    # ---------------- Projects ----------------
    if "project" in resume_lower:
        score += 10
    else:
        suggestions.append("Include academic or personal projects.")

    # ---------------- Experience ----------------
    if "experience" in resume_lower:
        score += 10
    else:
        suggestions.append("Include internships or work experience.")

    # ---------------- Certifications ----------------
    if "certification" in resume_lower:
        score += 5
    else:
        suggestions.append("Add certifications.")

    # ---------------- Resume Length ----------------
    pages = resume_data.get("no_of_pages", 0)

    if pages == 1:
        score += 10
    elif pages == 2:
        score += 8
    else:
        suggestions.append("Keep your resume between 1 and 2 pages.")

    # ---------------- ATS Score ----------------
    if ats_score is not None:

        if ats_score >= 90:
            score += 25

        elif ats_score >= 80:
            score += 20

        elif ats_score >= 70:
            score += 15

        elif ats_score >= 60:
            score += 10

        elif ats_score >= 40:
            score += 5

        else:
            suggestions.append(
                "Improve ATS compatibility by adding more Job Description keywords."
            )

    # Limit score
    score = min(score, 100)

    return score, suggestions