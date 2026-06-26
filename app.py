import streamlit as st
# Configure the Streamlit page
st.set_page_config(
    page_title="Resume Analyzer",
    layout="wide"
)

import os
import time
import datetime
import nltk
import pandas as pd
import plotly.express as px
from PIL import Image
from streamlit_tags import st_tags
from parser import pdf_reader, extract_resume_data
from pdf_utils import show_pdf
from resume_score import calculate_resume_score
from ats import (calculate_ats_score,extract_skills_from_text)
from database import (
    get_database_connection,
    create_tables,
    insert_data,
)
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

### Connect to database.
connection, cursor = get_database_connection()

if connection and cursor:
    create_tables(cursor)
else:
    st.error("Unable to connect to the database.")
    st.stop()

#
def run():
    # Display logo if available.
    try:
        img = Image.open("logo.png")
        st.image(img, width=180)
    except FileNotFoundError:
        st.warning("Logo file 'logo.png' not found.")

    # App title
    st.title("📄 Resume Analyzer")
    # Sidebar
    st.sidebar.title("Navigation")

    activities = ["User", "Admin"]
    choice = st.sidebar.selectbox(
        "Choose an option:",
        activities
    )

    # Developer information
    linkedin_url = "https://www.linkedin.com/in/your-profile/"  # Replace with your profile
    st.sidebar.markdown(
        f"**Developed by:** [Sushant]({linkedin_url})",
        unsafe_allow_html=True,
    )
    return choice


choice = run()

if choice == "User":
    st.markdown('''<h4 style='text-align: left; color: #021659;'> Upload your Resume and check your resume score</h4>''',
                 unsafe_allow_html=True)
    ## Upload your Resume.
    pdf_file = st.file_uploader("Upload your Resume",type=["pdf"])

    ## Paste job Description of Company.
    jd_text = st.text_area("Paste Job Description Here (Optional)",height=200)


    if pdf_file is not None:

        with st.spinner("Analyzing your resume..."):
            time.sleep(4)
        save_image_path = os.path.join("Uploaded_Resume", pdf_file.name)

        with open(save_image_path,"wb") as f:
            f.write(pdf_file.getbuffer())
        show_pdf(save_image_path)

        # Load skills database
        try:
            skills_df = pd.read_csv("skills.csv")
        except FileNotFoundError:
            st.error("skills.csv not found.")
            st.stop()

        #Extracting Resume data.
        resume_text = pdf_reader(save_image_path)
        ats_score = None

        resume_data = extract_resume_data(resume_text,save_image_path)

        if jd_text:
            ats_score = calculate_ats_score(resume_text,jd_text)

        missing_skills = []
        
        if resume_data:
            st.header("**Resume Analysis**")
            if jd_text:
                st.subheader("Job Description Preview")
                
                st.text_area(
                    "JD Content",
                    jd_text[:1000],height=200
                )

            st.success("Hello " + (resume_data["name"] or "Candidate"))
            st.subheader("** Your Basic Info")
            try:
                st.text("Name: "+resume_data["name"])
                st.text("Email: "+resume_data["email"])
                st.text("Contact: "+resume_data["mobile_number"])
                st.text("Resume pages: "+str(resume_data["no_of_pages"]))
            except:
                pass

            # Determine candidate level
            pages = resume_data["no_of_pages"]

            if pages <= 1:
                candidate_level = "Fresher"
            elif pages == 2:
                candidate_level = "Intermediate"
            else:
                candidate_level = "Experienced"

            st.info(f"Candidate Level: {candidate_level}")

            if jd_text:
                jd_skills = extract_skills_from_text(jd_text,skills_df)

                resume_skills = resume_data["skills"]

                resume_skills_lower = {skill.lower()
                                   for skill in resume_skills
                                }
            
                matching_skills = [skill
                               for skill in jd_skills
                               if skill.lower() in resume_skills_lower]

                missing_skills = [skill
                              for skill in jd_skills
                              if skill.lower() not in resume_skills_lower]
                
                if jd_skills:
                    skill_match_percent = round((len(matching_skills) / len(jd_skills)) * 100,2)
                else:
                    skill_match_percent = 0

                st.subheader("ATS Analysis")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("ATS Match Score",f"{ats_score}%")

                with col2:
                    st.metric("Skill Coverage",f"{skill_match_percent}%")

                if ats_score is not None:
                    if ats_score >= 80:
                        st.success("Excellent match for this job.")

                    elif ats_score >= 60:
                        st.info("Good match. Some improvements possible.")

                    else:
                        st.warning("Low match. Consider adding relevant skills.")
                       

                ## Display Matching Skills from uploaded Job-description.
                if matching_skills:
                    st.subheader("Matched Skills")
                    for skill in matching_skills:
                        st.markdown(f"✅ {skill}")

                ## Display Missing skills from uploaded job description.
                if missing_skills:
                    st.subheader("Missing Skills from JOB_Description")
                    st.warning("The following skills appear in the Job Description but not in your resume:")

                    for skill in missing_skills:
                        st.markdown(f"❌ {skill}")

                else:
                    st.success("Excellent! All detected JD skills are present in your resume.")
            
            # st.subheader("** Skills Recommendation**")
            ## Skill shows
            st.subheader("Your Current Skills:")

            for skill in resume_data["skills"]:
                st.markdown(f"{skill}")

            ## Recommendation of Skill required for prefered Job.
            recommended_field = resume_data.get("predicted_field", "Unknown")
            recommended_skills = []

            if recommended_field != "Unknown":
                st.success(f" Based on your resume, the predicted field is: {recommended_field}"
                           )

            # Get skills belonging to the predicted category
            recommended_skills = (skills_df.loc[skills_df["category"] == recommended_field,"skill"]
                                                .drop_duplicates()
                                                .tolist()
                                )

            # Remove skills the candidate already has.
            recommended_skills = [skill
                                  for skill in recommended_skills
                                  if skill not in resume_data["skills"]
                                ]

            st.subheader("Recommended Skills for your predictive field:")
            for skill in recommended_skills:
                st.markdown(f"{skill}")

             ## Insert into table
            ts = time.time()
            cur_date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
            cur_time = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
            timestamp = str(cur_date+" "+cur_time)
            

            ## Resume Writing Recommendation.
            st.subheader("Resume Quality Score")

            resume_score, suggestions = calculate_resume_score(resume_text,resume_data,ats_score)

            my_bar = st.progress(0)

            for i in range(0, resume_score + 1, 5):
                my_bar.progress(i)
                time.sleep(0.02)

            st.metric("Resume Score",f"{resume_score}/100")
            st.success(f"Your Resume Quality Score is {resume_score}/100")
            st.info("The score is calculated using resume structure, detected skills, ATS compatibility, and other quality indicators.")

            if suggestions:
                st.subheader("Suggestions to Improve Your Resume")
                for index, item in enumerate(suggestions, start=1):
                    st.markdown(f"{index}. 💡 {item}")

            st.balloons()

            ## AI Suggestion Feedback.
            st.subheader("AI Resume Feedback")
            feedback = []

            if jd_text:
                feedback.append(f"Your resume achieved an ATS score of {ats_score}%.")

                if missing_skills:
                    feedback.append("Consider learning: " + ", ".join(missing_skills[:5]))
                else:
                    feedback.append("Great! Your resume covers all detected JD skills.")
            else:
                feedback.append("No Job Description was provided, so ATS analysis was skipped.")

            feedback.append(f"Resume Quality Score: {resume_score}/100.")

            st.info("\n\n".join(feedback))

            ## Inserting Data into Database.
            saved = insert_data(connection=connection,cursor=cursor,
                                name=resume_data["name"],email=resume_data["email"],
                                res_score=resume_score,timestamp=timestamp,
                                no_of_pages=resume_data["no_of_pages"],
                                recommended_field=recommended_field,
                                candidate_level=candidate_level,skills=resume_data["skills"],
                                recommended_skills=recommended_skills,
                    )

            if saved:
                st.success("Analysis saved successfully.")
            
        else:
            st.warning(
                       "Could not confidently predict a field from the detected skills."
                      )
## Admin side.
else:
    st.success("Welcome to Admin Side")
    #st.sidebar.subheader("ID/Password Require")

    ad_user = st.text_input("Username")
    ad_password = st.text_input("Password",type="password")
    if st.button("Login"):
        if ad_user == os.getenv("ADMIN_USER") and ad_password == os.getenv("ADMIN_PASSWORD"):
            st.success("Welcome Mr Sk")

            #Display Data.
            cursor.execute('''SELECT*FROM user_data''')
            data = cursor.fetchall()
            st.header("Users Data")
            df = pd.DataFrame(data,columns=["ID","Name","Email",
                                            "Resume Score","Timestamp","Total Pages",
                                            "Predicted Field","User Level",
                                            "Actual Skill","Recommended Skill"])
            st.dataframe(df)
            st.download_button(
                label="Download Report",
                data=df.to_csv(index=False),
                file_name="User_Data.csv",
                mime="text/csv"
            )
            ## Admin Side Data.
            query = "select * from user_data;"
            plot_data = pd.read_sql(query,connection)

            ## Pie chart for predicted field recommendation.
            st.subheader("📊 Pie Chart for Predicted Field Recommendation")

            field_counts = plot_data["Predicted_field"].value_counts()

            fig = px.pie(names=field_counts.index,
                         values=field_counts.values,
                         title="Predicted Field Distribution"
                        )

            st.plotly_chart(fig)
        
        else:
            st.error("Wrong ID & Password")
           


