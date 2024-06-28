from dotenv import load_dotenv
load_dotenv()
import streamlit as st 
import os
import io
import base64
from PIL import Image
import pdf2image
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input_text, pdf_content[0], prompt])
    
    # Print response and its attributes for inspection
    print(response)
    print(dir(response))
    
    # Adjust based on the actual response structure
    # Example: Assuming the response has a 'text' attribute
    if hasattr(response, 'text'):
        return response.text
    else:
        raise ValueError("Response object does not have 'text' attribute or similar")

def input_pdf_setup(uploaded_file):
    images = pdf2image.convert_from_bytes(uploaded_file.read())
    first_page = images[0]
    return process_pdf(first_page)

# Convert to bytes
def process_pdf(first_page):
    if first_page:
        # Create an in-memory byte array
        img_byte_arr = io.BytesIO()
        
        # Save the first page of the PDF as a JPEG image in the byte array
        first_page.save(img_byte_arr, format='JPEG')
        
        # Get the byte array value
        img_byte_arr = img_byte_arr.getvalue()
        
        # Encode the byte array to base64
        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            }
        ]
        
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Streamlit

st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")
input_text = st.text_area("Job Description: ", key="input")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

input_prompt1 = """
You are an experienced Technical Human Resource Manager, your task is to review the provided resume against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
the job description. First, the output should come as a percentage and then keywords missing and lastly, final thoughts.
"""

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")
    
    submit1 = st.button("Tell Me About the Resume")
    submit3 = st.button("Percentage match")
    
    if submit1:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, input_prompt1)
        st.subheader("The Response is")
        st.write(response)

    elif submit3:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, input_prompt3)
        st.subheader("The Response is")
        st.write(response)
else:
    st.write("Please upload the resume")
