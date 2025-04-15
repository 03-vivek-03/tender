import streamlit as st
import cohere
import PyPDF2

# Initialize Cohere client
co = cohere.ClientV2(api_key="okYrKAw1OPZoMnOSCR6rUVO2cbSulB4gCmuo04UY")  # Replace with your key

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def stream_summary_from_cohere(text):
    prompt = (
        "Summarize this tender document and give all the important information "
        "and values required to understand the tender. Include all the details "
        "such as tender reference number and ID, tender fee, tender meeting dates and venue, EMD, pre-bid dates and links, Modules, workforce required, eligibility criteria, marking criteria, Performance Security, "
        "CSP Details, location, contract period, implementation period and phases (TAT), organisation, Payment Terms, estimated cost, contact details, submission(Online, Physical) and selection methods(QCBS or L1 selection), existing IHMS Application, etc.\n\n"
        f"{text}"
    )

    response = co.chat_stream(
        model="command-a-03-2025",
        messages=[{"role": "user", "content": prompt}]
    )

    for chunk in response:
        if chunk and chunk.type == "content-delta":
            yield chunk.delta.message.content.text

# Set page config
st.set_page_config(page_title="Tender Summarizer", page_icon="📄")

# UI content
st.title("📄 Tender Document Summarizer")
st.markdown("Upload a **tender PDF** and get a concise summary with all key information extracted.")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Extracting text from PDF..."):
        text = extract_text_from_pdf(uploaded_file)

    if len(text.strip()) < 100:
        st.error("The uploaded PDF has very little text or is not extractable.")
    else:
        st.success("✅ Text extracted! Generating summary...\n")
        
        # Add a placeholder to dynamically update the summary
        summary_placeholder = st.empty()
        summary_text = ""
        for chunk in stream_summary_from_cohere(text):
            summary_text += chunk
            summary_placeholder.markdown(summary_text)
        
        # Store the final summary in session state for later use (if needed)
        st.session_state["summary"] = summary_text
else:
    st.info("Please upload a tender PDF file to begin.")

# Footer and close centered div
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color: gray;'>Designed by Medimaze AI Team</p></div>",
    unsafe_allow_html=True,
)
