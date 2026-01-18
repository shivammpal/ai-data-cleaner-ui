import streamlit as st
import requests
import time

API_BASE = "http://72.61.244.118:8001"   # or domain if you setup nginx

st.set_page_config(page_title="AI Data Cleaning Agent", layout="centered")
st.title("🧹 AI Data Cleaning Agent")

file = st.file_uploader("Upload CSV file", type=["csv"])
instructions = st.text_area("Cleaning Instructions", "Auto clean best practices")

# -------- START JOB --------
if st.button("Start Cleaning"):
    if not file:
        st.warning("Please upload a CSV file")
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
                st.success(f"Job started: {job_id}")

# -------- CHECK STATUS + DOWNLOAD --------
if "job_id" in st.session_state:
    job_id = st.session_state["job_id"]

    st.info("Checking job status...")

    status_placeholder = st.empty()

    while True:
        time.sleep(3)

        s = requests.get(f"{API_BASE}/job-status/{job_id}").json()
        status = s.get("status")

        status_placeholder.write(f"Status: **{status}**")

        if status == "completed":
            st.success("Cleaning finished ✅")

            dl = requests.get(f"{API_BASE}/download/{job_id}")

            st.download_button(
                "⬇ Download Cleaned CSV",
                data=dl.content,
                file_name="cleaned.csv",
                mime="text/csv",
            )
            break

        if status == "failed":
            st.error("Job failed ❌")
            break
