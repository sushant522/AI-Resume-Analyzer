## Handle all MYSQL databse Operations.

import pymysql
import os
import streamlit as st
from dotenv import load_dotenv
# Load Environment Variable from .env.
load_dotenv()


def get_database_connection():
    """
    Connect to the MySQL database.
    """
    try:
        connection = pymysql.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            port=int(os.getenv("MYSQL_PORT")),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            charset="utf8mb4",
            autocommit=True,
            ssl={"ssl": {}},
        )

        cursor = connection.cursor()
        return connection, cursor

    except pymysql.MySQLError as e:
        st.error(f"❌ Database connection failed: {e}")
        return None, None


def create_tables(cursor):
    """
    Create the user_data table if it does not already exist.
    """
    table_sql = """
    CREATE TABLE IF NOT EXISTS user_data (
        ID INT NOT NULL AUTO_INCREMENT,
        Name VARCHAR(255),
        Email_id VARCHAR(500),
        Resume_score VARCHAR(8),
        Timestamp VARCHAR(50),
        Page_no VARCHAR(5),
        Predicted_field VARCHAR(100),
        User_level VARCHAR(100),
        Actual_skills TEXT,
        Recommended_skills TEXT,
        PRIMARY KEY (ID)
    )
    """
    cursor.execute(table_sql)


def insert_data(
    connection,
    cursor,
    name,
    email,
    res_score,
    timestamp,
    no_of_pages,
    recommended_field,
    candidate_level,
    skills,
    recommended_skills
):

    """
    Insert resume analysis data into the user_data table.
    Args:
        connection: Active MySQL connection.
        cursor: Database cursor.
        name : Candidate's name.
        email : Candidate's email.
        resume_score : Resume score.
        timestamp : Analysis timestamp.
        page_count : Number of resume pages.
        predicted_field : Predicted career field.
        candidate_level : Candidate experience level.
        skills : Extracted skills.
        recommended_skills : Suggested skills.

    """
    try:
        insert_sql = """
        INSERT INTO user_data (
            Name,
            Email_id,
            Resume_score,
            Timestamp,
            Page_no,
            Predicted_field,
            User_level,
            Actual_skills,
            Recommended_skills
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            name,
            email,
            str(res_score),
            timestamp,
            str(no_of_pages),
            recommended_field,
            candidate_level,
            ", ".join(skills) if isinstance(skills, list) else str(skills),
            ", ".join(recommended_skills)
            if isinstance(recommended_skills, list)
            else str(recommended_skills),
        )

        cursor.execute(insert_sql, values)
        connection.commit()

        return True

    except pymysql.MySQLError as e:
        st.error(f"❌ Failed to insert data: {e}")
        return False