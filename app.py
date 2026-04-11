import streamlit as st
import subprocess
import tempfile
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)

SUPPORTED_LANGUAGES = ["Python", "Java", "C", "C++", "JavaScript"]

# -------------------------------
# Function: Static Analysis
# Only works for Python via pylint
# -------------------------------
def run_static_analysis(code, language):
    if language != "Python":
        return "ℹ️ Static analysis (Pylint) is only available for Python."

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
        tmp.write(code.encode())
        tmp.close()
        result = subprocess.run(
            ["pylint", tmp.name, "--disable=all", "--enable=E,W"],
            capture_output=True,
            text=True
        )
        return result.stdout or "✅ No major issues found by Pylint."


# -------------------------------
# Function: AI Code Review
# -------------------------------
def ai_code_review(code, language):
    prompt = f"""
You are a senior software engineer specializing in code review.

Analyze the following {language} code and provide:

1. **Bug Detection**: List all bugs, errors, or crashes you find
2. **Code Quality Issues**: Point out bad practices or inefficiencies
3. **Security Issues**: Flag any security vulnerabilities
4. **Corrected Code**: Provide the fixed version of the code
5. **Overall Rating**: Rate as Good / Needs Work / Poor

Be specific and beginner-friendly in your explanations.

```{language}
{code}
```
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content


# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Code Reviewer & Bug Detector")
st.markdown("Powered by Gemini 1.5 Flash + Pylint | Supports Python, Java, C, C++, JavaScript")
st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    language = st.selectbox("Select Language:", SUPPORTED_LANGUAGES)
    code_input = st.text_area("Paste your code here:", height=350)
    analyze_btn = st.button("🔍 Analyze Code", use_container_width=True)

with col2:
    if analyze_btn:
        if code_input.strip() == "":
            st.warning("Please enter some code first!")
        else:
            with st.spinner("Analyzing your code..."):

                st.subheader("📋 Static Analysis (Pylint)")
                pylint_output = run_static_analysis(code_input, language)
                st.code(pylint_output, language="bash")

                st.subheader("🤖 AI Review")
                ai_output = ai_code_review(code_input, language)
                st.markdown(ai_output)
    else:
        st.info("👈 Paste your code and hit Analyze to get started.")