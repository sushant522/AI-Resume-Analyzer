import streamlit as st
import base64

def show_pdf(pdf_source):
    """
    Display a PDF in Streamlit.

    Parameters:
        pdf_source: Either a file path (str) or an uploaded file object.
    """
    try:
        if isinstance(pdf_source, str):
            with open(pdf_source, "rb") as f:
                pdf_bytes = f.read()
        else:
            # For Streamlit UploadedFile objects
            pdf_bytes = pdf_source.read()
            pdf_source.seek(0)  # Reset pointer for later use if needed

        base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

        pdf_display = f"""
        <embed
            src="data:application/pdf;base64,{base64_pdf}"
            width="100%"
            height="800"
            type="application/pdf">
        """

        st.markdown(pdf_display, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Unable to display PDF: {e}")