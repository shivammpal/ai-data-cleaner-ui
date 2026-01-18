import streamlit as st
import requests

st.set_page_config(page_title="AI Data Cleaning Agent", layout="centered")

st.title("🧹 AI Data Cleaning Agent")
st.write("Upload your file and get cleaned data using AI.")

# 👉 PUT YOUR N8N WEBHOOK URL HERE
N8N_WEBHOOK_URL = "https://n8n.mbaipartnerspf.com/webhook/clean-data"

file = st.file_uploader("Upload CSV file", type=["csv"])
instructions = st.text_area(
    "Cleaning Instructions",
    placeholder="Example: remove duplicates, normalize emails, fix phone numbers"
)

if st.button("Clean My Data"):
    if not file or not instructions:
        st.warning("Please upload file and provide instructions.")
    else:
        with st.spinner("Processing your file..."):
            try:
                files = {"file": (file.name, file.getvalue(), "text/csv")}
                data = {"instructions": instructions}

                res = requests.post(N8N_WEBHOOK_URL, files=files, data=data, timeout=300)

                if res.status_code == 200:
                    st.success("Cleaning completed!")
                    st.download_button(
                        label="Download Cleaned File",
                        data=res.content,
                        file_name="cleaned_" + file.name,
                        mime="text/csv"
                    )
                else:
                    st.error("Server error. Please try again later.")

            except Exception as e:
                st.error(str(e))
