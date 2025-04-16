import streamlit as st
import cohere
import PyPDF2
from docx import Document
from io import BytesIO
from docx.shared import Pt

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
        """You are an expert in understanding and summarizing government tender documents.

            Summarize the following tender document by extracting and presenting all the critical details required for a complete understanding of the tender. Ensure the summary includes (but is not limited to) the following information:

            - Tender Reference Number and ID  
            - Name of the Organization/Authority  
            - Tender Fee  
            - Estimated Tender Value or Project Cost  
            - EMD (Earnest Money Deposit) Details  
            - Pre-bid Meeting Dates, Venue, and Registration/Link Details  
            - Tender Meeting Dates and Venues (if different from Pre-bid)  
            - Modules or Work Packages Covered in the Tender  
            - Workforce Requirements (if mentioned)  
            - Eligibility Criteria for Bidders  
            - Technical and Financial Marking/Scoring Criteria  
            - Performance Security Requirements  
            - Cloud Service Provider (CSP) Details, if applicable  
            - Project Location(s)  
            - Contract Period/Duration  
            - Implementation Timeline and Phases (TAT)  
            - Details about any existing IHMS or related Application  
            - Payment Terms and Schedule  
            - Submission Methods (Online, Physical, Hybrid)  
            - Selection Methodology (e.g., QCBS, L1, etc.)  
            - Contact Information of the Tender Issuer (Phone, Email, Address)

            Present the summary in a clear, structured format using bullet points or headings.

            Tender Document:\n\n"""
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
    with st.spinner("File uploaded successfully!✅"):
        text = extract_text_from_pdf(uploaded_file)

    if len(text.strip()) < 100:
        st.error("The uploaded PDF has very little text or is not extractable.")
    else:
        st.success("Generating summary...\n")
        
        # Add a placeholder to dynamically update the summary
        summary_placeholder = st.empty()
        if "summary" not in st.session_state:
            summary_text = ""
            for chunk in stream_summary_from_cohere(text):
                summary_text += chunk
                summary_placeholder.markdown(summary_text)
            st.session_state["summary"] = summary_text
        else:
            summary_text = st.session_state["summary"]
            summary_placeholder.markdown(summary_text)

        # Generate Word document with formatting
        doc = Document()
        style = doc.styles["Normal"]
        style.font.size = Pt(11)

        doc.add_heading("Tender Summary", level=1)

        # Process the summary line by line
        for line in summary_text.splitlines():
            line = line.strip()
            if not line:
                doc.add_paragraph("")  # Preserve blank lines
                continue

            # Handle markdown-style headings
            if line.startswith("####"):
                doc.add_heading(line.replace("####", "").strip(), level=4)
            elif line.startswith("###"):
                doc.add_heading(line.replace("###", "").strip(), level=3)
            else:
                # Split the line based on '**' to handle bold text
                paragraph = doc.add_paragraph()
                segments = line.split('**')
                
                for i, segment in enumerate(segments):
                    if i % 2 == 1:  # This part should be bold (because it's between '**')
                        paragraph.add_run(segment).bold = True
                    else:  # Normal text (no bold)
                        paragraph.add_run(segment)

        # Save to BytesIO buffer
        word_buffer = BytesIO()
        doc.save(word_buffer)

        word_buffer.seek(0)

        # Download button
        st.download_button(
            label="📥 Download Summary as Word Document",
            data=word_buffer,
            file_name="Tender_Summary.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
else:
    st.info("Please upload a tender PDF file to begin.")

# Footer and close centered div
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color: gray;'>Designed by Medimaze AI Team</p></div>",
    unsafe_allow_html=True,
)
