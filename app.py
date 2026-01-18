import streamlit as st
import requests
import time

st.set_page_config(page_title="AI Data Cleaning Agent", layout="centered")

st.title("🧹 AI Data Cleaning Agent (Async)")

API_BASE = "http://72.61.244.118:8001"   # your FastAPI IP
# If using domain later, replace with https://api.domain.com

file = st.file_uploader("Upload CSV file", type=["csv"])
instructions = st.text_area(
    "Cleaning Instructions",
    placeholder="Example: normalize phone and email, remove duplicates, fill missing values"
)

if st.button("Start Cleaning"):
    if not file or not instructions:
        st.warning("Upload file and enter instructions.")
    else:
        with st.spinner("Submitting job..."):
            files = {"file": (file.name, file.getvalue(), "text/csv")}
            data = {"instructions": instructions}

            res = requests.post(f"{API_BASE}/clean-job", files=files, data=data)

            if res.status_code != 200:
                st.error(res.text)
            else:
                job_id = res.json()["job_id"]
                st.session_state["job_id"] = job_id
                st.success(f"Job submitted: {job_id}")

# ---------------- STATUS POLLING ----------------

if "job_id" in st.session_state:
    job_id = st.session_state["job_id"]

    st.info("Processing… checking status every 3 seconds")

    status_placeholder = st.empty()
    progress_bar = st.progress(0)

    for i in range(60):  # ~3 minutes
        time.sleep(3)

        s = requests.get(f"{API_BASE}/job-status/{job_id}").json()
        status = s.get("status")

        status_placeholder.write(f"Status: **{status}**")
        progress_bar.progress(min((i+1)*2, 100))

        if status == "completed":
            st.success("Cleaning completed!")

            dl = requests.get(f"{API_BASE}/download/{job_id}")

            st.download_button(
                label="⬇ Download Cleaned File",
                data=dl.content,
                file_name="cleaned_" + file.name,
                mime="text/csv"
            )
            break

        if status == "failed":
            st.error("Job failed. Check backend logs.")
            break
