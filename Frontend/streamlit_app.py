import streamlit as st
import requests

# FastAPI server URL
FASTAPI_URL = "http://localhost:8000/api"

# Initialize session state
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False

if "challenge_generated" not in st.session_state:
    st.session_state.challenge_generated = False

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

if "challenge" not in st.session_state:
    st.session_state.challenge = ""

# Title
st.title("📚 Study Material Uploader with QR Processing")

# --- Upload File Section ---
uploaded_file = st.file_uploader("Upload PDF, Image, Audio, or Text File", 
                                 type=["pdf", "png", "jpg", "jpeg", "txt", "mp3", "wav"])

if uploaded_file:
    st.session_state.uploaded_file = uploaded_file

if st.session_state.uploaded_file and not st.session_state.file_uploaded:
    st.write("File uploaded successfully!")

    files = {
        "file": (
            st.session_state.uploaded_file.name,
            st.session_state.uploaded_file.getvalue(),
            st.session_state.uploaded_file.type
        )
    }

    response = requests.post(f"{FASTAPI_URL}/upload/", files=files)

    if response.status_code == 200:
        st.success("File processed successfully!")
        st.json(response.json())
        st.session_state.file_uploaded = True
    else:
        st.error("Failed to process file.")
        try:
            st.json(response.json())
        except Exception:
            st.write(response.text)

# --- Coding Challenge Section ---
st.header("🛠️ Generate Coding Challenge")

language = st.selectbox("Select Language", ["python", "javascript", "java"])
problem_type = st.radio("Select Challenge Type", ['Buggy Code', 'New Problem', 'Incomplete Code'])
difficulty = st.selectbox("Select Difficulty Level", ['Easy', 'Medium', 'Hard'])

challenge_map = {
    "Buggy Code": "bug_finding",
    "New Problem": "new_code",
    "Incomplete Code": "missing_code"
}

if st.button("Generate Challenge"):
    if not st.session_state.file_uploaded:
        st.warning("Please upload a file first before generating the challenge.")
    else:
        challenge_url = f"{FASTAPI_URL}/coding-exercise/"
        payload = {
            "language": language,
            "problem_type": challenge_map[problem_type],
            "query": "example_query",
            "difficulty": difficulty.lower()
        }

        response = requests.post(challenge_url, json=payload)

        if response.status_code == 200:
            challenge = response.json().get("challenge", "No challenge found.")
            st.session_state.challenge = challenge
            st.session_state.challenge_generated = True
            st.success("Challenge generated successfully!")
        else:
            st.error("Failed to generate challenge.")
            try:
                st.json(response.json())
            except Exception:
                st.write(response.text)

# Display challenge
if st.session_state.challenge_generated:
    st.write("### 💡 Generated Challenge")
    st.code(st.session_state.challenge, language=language)
