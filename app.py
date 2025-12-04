import streamlit as st
import os
from supporting_functions import (
    extract_video_id,
    get_transcript,
    translate_transcript,
    generate_notes,
    get_important_topics,
    create_chunks,
    create_vector_store,
    rag_answer,
    generate_pdf,
)

# Initialize session state variables at the top level
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None
if "pdf_filename" not in st.session_state:
    st.session_state.pdf_filename = None

# ADDED: Initialize session state for data persistence
if "video_id" not in st.session_state:
    st.session_state.video_id = None
if "import_topics" not in st.session_state:
    st.session_state.import_topics = None
if "notes" not in st.session_state:
    st.session_state.notes = None

# Variables for local use in the current script run
full_transcript = None
task_option = None

# --- Sidebar (Inputs) ---
with st.sidebar:
    st.title("🎬 VidSynth AI")
    st.markdown("---")
    st.markdown("Transform any YouTube video into key topics, a podcast, or a chatbot.")
    st.markdown("### Input Details")

    youtube_url = st.text_input(
        "YouTube URL", placeholder="https://www.youtube.com/watch?v=..."
    )
    language = st.text_input(
        "Video Language Code", placeholder="e.g., en, hi, es, fr", value="en"
    )

    task_option = st.radio(
        "Choose what you want to generate:", ["Chat with Video", "Notes For You"]
    )

    submit_button = st.button("✨ Start Processing")
    st.markdown("---")

# --- Main Page ---
st.title("YouTube Content Synthesizer")
st.markdown("Paste a video link and select a task from the sidebar.")

# --- Processing Flow ---
if submit_button:
    # Clear PDF and Notes data for a new submission
    st.session_state.pdf_bytes = None
    st.session_state.pdf_filename = None
    st.session_state.import_topics = None
    st.session_state.notes = None

    if youtube_url and language:
        # STORE video_id in session state
        st.session_state.video_id = extract_video_id(youtube_url)
        video_id = st.session_state.video_id  # Use local variable for convenience

        if not video_id:
            st.error("Invalid YouTube URL. Please enter a valid video link.")
        else:
            with st.spinner("Step 1/3: Fetching Transcript..."):
                full_transcript = get_transcript(video_id, language)

            if not full_transcript:
                st.error(
                    "Failed to fetch transcript. Please try again later or check video accessibility."
                )
            else:
                if language.strip().lower() != "en":
                    with st.spinner(
                        "Step 1.5/3: Translating Transcript into English, please wait..."
                    ):
                        translated_transcript = translate_transcript(full_transcript)
                    if not translated_transcript:
                        st.error(
                            "Translation failed. Please verify the language code and try again."
                        )
                        full_transcript = None
                    else:
                        full_transcript = translated_transcript

                if full_transcript:
                    # ---- Notes Path ----
                    if task_option == "Notes For You":
                        with st.spinner("Step 2/3: Extracting Important Topics..."):
                            # STORE important_topics in session state
                            st.session_state.import_topics = get_important_topics(
                                full_transcript
                            )

                        st.subheader("📌 Important Topics")
                        st.write(st.session_state.import_topics)
                        st.markdown("---")

                        with st.spinner("Step 3/3: Generating Notes for you..."):
                            # STORE notes in session state
                            st.session_state.notes = generate_notes(full_transcript)

                        st.subheader("📝 Notes for you")
                        st.write(st.session_state.notes)
                        st.success("✅ Summary and Notes Generated Successfully!")

                    # ---- Chat Path ----
                    elif task_option == "Chat with Video":
                        with st.spinner(
                            "Step 2/3: Creating Chunks and Vector Store..."
                        ):
                            doc_chunks = create_chunks(full_transcript)
                            vectorstore = create_vector_store(doc_chunks)
                            st.session_state.vector_store = vectorstore
                        st.session_state.messages = []
                        st.success("Video is ready for chat.")


# --- PDF Download and Generation Logic (MOVED OUTSIDE 'if submit_button') ---

# Check if notes have been successfully generated and stored in session state
if (
    st.session_state.get("import_topics")
    and st.session_state.get("notes")
    and st.session_state.get("video_id")
    # You may also want to ensure 'Notes For You' was the selected task
):
    # This renders the "Generate PDF" button and info section
    st.markdown("---")
    col1, col2 = st.columns([3, 1])

    with col1:
        st.info("💡 Download your notes as a PDF to save for later!")

    with col2:
        generate_pdf_clicked = st.button("📥 Generate PDF", key="gen_pdf")

    # Handle the PDF generation on button click
    if generate_pdf_clicked:
        with st.spinner("Generating PDF..."):
            # RETRIEVE data from session state
            video_title = f"YouTube Video ({st.session_state.video_id})"
            pdf_path = generate_pdf(
                video_title, st.session_state.import_topics, st.session_state.notes
            )
            if pdf_path:
                with open(pdf_path, "rb") as pdf_file:
                    st.session_state.pdf_bytes = pdf_file.read()
                st.session_state.pdf_filename = os.path.basename(pdf_path)
                # Rerun to make the st.download_button appear with the new data
                st.rerun()
            else:
                st.error("PDF generation failed.")

    # Always show download button if ready (appears on the run *after* st.rerun())
    if st.session_state.get("pdf_bytes"):
        st.download_button(
            label="💾 Save PDF",
            data=st.session_state.pdf_bytes,
            file_name=st.session_state.pdf_filename,
            mime="application/pdf",
        )

# --- Chatbot Session ---
if (
    st.session_state.get("vector_store") is not None
    and task_option == "Chat with Video"
):
    st.divider()
    st.subheader("Chat with Video")

    # Show chat history
    for message in st.session_state.get("messages", []):
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    prompt = st.chat_input("Ask me anything about the video.")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            response = rag_answer(prompt, st.session_state.vector_store)
            st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
