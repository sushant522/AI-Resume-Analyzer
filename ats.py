from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

## Function to calculate the ATS-matching score with given JOB-Description.
def calculate_ats_score(resume_text, jd_text):
    """
    Calculate similarity between resume and job description.
    Returns score out of 100.
    """

    documents = [resume_text, jd_text]

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    vectors = vectorizer.fit_transform(
        documents
    )

    similarity = cosine_similarity(
        vectors[0:1],
        vectors[1:2]
    )[0][0]

    return round(similarity * 100, 2)

## Function For missing skill detection for JOB.
def extract_skills_from_text(text, skills_df):
    """
    Extract skills from any text using skills.csv
    """

    text = text.lower()

    found_skills = []

    for skill in skills_df["skill"]:

        pattern = rf"\b{re.escape(skill.lower())}\b"

        if re.search(pattern, text):
            found_skills.append(skill)

    return list(dict.fromkeys(found_skills))