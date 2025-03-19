import streamlit as st
import os
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio_module import Portfolio
from utils import clean_text
import subprocess

# Force upgrade SQLite for ChromaDB
os.environ["LD_LIBRARY_PATH"] = "/home/adminuser/.local/lib"
subprocess.run(["pip", "install", "--upgrade", "--force-reinstall", "pysqlite3-binary"], check=True)
subprocess.run(["pip", "install", "--upgrade", "--force-reinstall", "pysqlite3"], check=True)

# Set environment variables
os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
os.environ["GROQ_API_KEY"] = "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"

# Streamlit UI Styling
st.set_page_config(layout='wide', page_title="Cold Email Generator")
st.markdown(
    """
        <style>

          /* Responsive Design */
            @media (max-width: 768px) {
                .stApp { padding: 10px; }
                .stTextInput > div { width: 100% !important; }
                .stButton > button { width: 100%; }
            }

            /* Page Background and Thick Border */
            /* Full Page Background and Thick Border */
            html, body, .stApp {
            background-color: gray !important;  /* Ensures full-page black background */
            color: white;
            font-family: 'Arial', sans-serif;
            border: 10px solid black; /* Thick border around the entire page */
            padding: 20px;
            margin: 0;
            height: 100%;
        }


            .stTextInput {
            display: flex;
            justify-content: center;
            width: 100%;
        }

        .stTextInput > div {
            display: flex;
            justify-content: center;
            width: 70%;  /* Ensures the input container is 70% */
        }

        .stTextInput > div > div {
            width: 100%;  /* Makes sure the inner container also takes 70% */
        }

        .stTextInput > div > div > input {
            background-color: #222;
            color: #fff;
            border: 2px solid #00ffcc;
            border-radius: 8px;
            padding: 10px;
            width: 100%;  /* Ensures input field fills the container */
            text-align: center;
        }


        .stButton {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }
        .stButton > button {
            background: linear-gradient(45deg, #0000, #008080);
            color: black;
            font-weight: bold;
            border: 3px solid black;
            border-radius: 8px;
            padding: 10px 20px;
            transition: all 0.3s ease-in-out;
        }
        .stButton > button:hover {
            background: linear-gradient(45deg, #00ffcc, #006666); /* Same as normal */
            transform: scale(1.1); /* Slight pop effect */
            border: 2px solid #00ffcc; /* Ensure border color stays same */
            box-shadow: 0px 0px 15px #00ffcc; /* Subtle glow */
        }
        .stButton > button:active {
            transform: scale(1.1);
            box-shadow: 0px 0px 15px black;
        }
        .stCode {
            border: 2px solid #00ffcc;
            border-radius: 8px;
            padding: 10px;
            background-color: #111;
            color: #00ffcc;
            transition: all 0.3s ease-in-out;
        }
        .stCode:hover {
            border-color: black;
            box-shadow: 0px 0px 10px black;
        }
        .stTitle, .stTextInput label, .stButton > button {
            text-shadow: 3px 3px 15px rgba(255, 255, 255, 0.8);
        }
        .stApp {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            width: 100vw;
            animation: fadeIn 2s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
        """
        <div style="display: flex; flex-direction: column; gap: 0px;">
            <hr style='border: 3px solid black; margin: 0px;'>
            <hr style='border: 10px solid white; margin: 0px;'>
            <hr style='border: 3px solid black; margin: 0px;'>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<h1 style='text-align: center; animation: fadeIn 2s ease-in-out;'>📧 COLD EMAIL GENERATOR📧</h1>", unsafe_allow_html=True)

def create_streamlit_app(llm, portfolio, clean_text):
    st.markdown(
    "<h5 style='text-align: center; font-weight: bold; color: white;'>Enter a JOB OPENING URL BELOW:</h5>",
    unsafe_allow_html=True)
    url_input = st.text_input("", value="https://somejob_opeing_url.com")

    submit_button = st.button("🚀 Generate Email")
    st.markdown(
        """
        <div style="display: flex; flex-direction: column; gap: 0px;">
            <hr style='border: 3px solid black; margin: 0px;'>
            <hr style='border: 3px solid white; margin: 0px;'>
            <hr style='border: 3px solid black; margin: 0px;'>
        </div>
        """,
        unsafe_allow_html=True
    )

    if submit_button:
        if not url_input.strip():
            st.warning("⚠️ Please enter a valid URL.")
            return
        
        try:
            loader = WebBaseLoader(url_input)
            data = loader.load()[0].page_content
            cleaned_data = clean_text(data)
            
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(cleaned_data)
            
            if not jobs:
                st.warning("❌ No jobs found in the extracted content.")
                return
            st.markdown(
                 "<h5 style='text-align: left; font-weight: bold; color: white;'> COLD EMAILS GENERATED BY 🤖LLAMA-3.1-8b-INST🤖:</h5>",
                 unsafe_allow_html=True
                )

            # Initialize stop flag and generated emails in session state
            if "stop_generating" not in st.session_state:
                st.session_state.stop_generating = False
            if "generated_emails" not in st.session_state:
                st.session_state.generated_emails = []



            

            # Keep a local copy of generated emails to ensure correct numbering
            generated_emails = list(st.session_state.generated_emails)  

            for job in jobs:
                if st.session_state.stop_generating:
                    st.warning("🚨 Email generation stopped!")
                    break  # Stop generating emails when button is clicked
                if len(generated_emails) >= 10:
                    break

                skills = job.get('skills', [])
                links = portfolio.query_links(skills) if skills else []
            
                email = llm.write_mail(job, links)
                generated_emails.append(email)  # Append new email to local list

            

                # Update session state after all new emails are added
                st.session_state.generated_emails = generated_emails

                # Display all stored emails with correct numbering
            for idx, email in enumerate(st.session_state.generated_emails, start=1):
                st.markdown(f"### Email {idx}  >📧")
                st.code(email, language='markdown')
                st.markdown("<hr style='border: 2px solid white;'>", unsafe_allow_html=True)

            # 🛑 Stop Button - Placed at the End of the Page
            st.markdown("<br><hr><br>", unsafe_allow_html=True)  # Adds spacing and a separator for clarity

            # Define stop button here before checking its value
            stop_button = st.button("TAP TO CLOSE", key="stop_button", help="Click to stop email generation")

            if stop_button:
                 st.session_state.stop_generating = True

        except Exception as e:
            st.error(f"🔥 An error occurred: {str(e)}")

if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    
    create_streamlit_app(chain, portfolio, clean_text)
