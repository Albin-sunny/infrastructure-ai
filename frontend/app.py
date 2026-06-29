import streamlit as st
import requests
import os
import uuid

st.set_page_config(
    page_title="InfraGuard AI",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ InfraGuard AI")
st.caption("AI-Powered Infrastructure Inspection & Engineering Assistant")

st.divider()

# --- Crack Detection Section ---
st.header("🔍 Crack Detection")

uploaded_file = st.file_uploader(
    "Upload Infrastructure Image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    st.image(
        uploaded_file,
        caption="Uploaded Image",
        use_container_width=True
    )

    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type
        )
    }

    try:
        with st.spinner("Analyzing image..."):
            response = requests.post(
                "http://127.0.0.1:8000/detect",
                files=files
            )
            response.raise_for_status()
            result = response.json()

        st.success("Detection Complete")
        st.subheader("📊 Detection Results")

        col1, col2, col3 = st.columns(3)
        col1.metric("Crack Count", result["defect_count"])
        col2.metric("Area %", round(result["crack_area_percent"], 2))
        col3.metric("Confidence", round(result["confidence"], 2))

        st.write("**Defect Type:**", result["defect_type"])

        severity = result["severity"]
        if severity == "High":
            st.error(f"Severity: {severity}")
        elif severity == "Medium":
            st.warning(f"Severity: {severity}")
        else:
            st.success(f"Severity: {severity}")

        st.write("**Risk Level:**", result["risk_level"])

        st.subheader("🛠 Repair Recommendation")
        st.info(result["repair_recommendation"])

        pdf_path = result.get("report_path")
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📄 Download Inspection Report",
                    data=pdf_file,
                    file_name="inspection_report.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning(f"PDF file not found: {pdf_path}")

    except Exception as e:
        st.error(f"Detection Error: {e}")

st.divider()

# --- Engineering Assistant ---
st.header("🤖 Engineering Assistant")


if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

question = st.text_input("Ask an engineering question")

if st.button("Ask"):
    if question.strip() == "":
        st.warning("Please enter a question.")
    else:
        try:
            response = requests.post(
                "http://127.0.0.1:8000/inspection-chat",
                json={"question": question
                      ,"conversation_id":st.session_state.conversation_id
                      
                      }
            )
            response.raise_for_status()
            result = response.json()
            answer = result["answer"]

            st.session_state.chat_history.append(
                {
                    "question": question,
                    "answer": answer
                }
            )
        except Exception as e:
            st.error(f"Chat Error: {e}")

if st.session_state.chat_history:
    st.subheader("💬 Chat History")
    for chat in reversed(st.session_state.chat_history):
        st.markdown(f"**Question:** {chat['question']}")
        st.markdown(f"**Answer:** {chat['answer']}")
        st.divider()