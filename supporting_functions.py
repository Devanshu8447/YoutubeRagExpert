import re
import os
import time
from datetime import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()


# Function to extract video ID from a Youtube URL (Helper Function)
def extract_video_id(url):
    """
    Extracts the yt video id from any valid yt url.
    """
    match = re.search(r"(?:v=|V)([0-9A-Za-z_-]{11}).*", url)
    if match:
        return match.group(1)
    st.error("Invalid Youtube URL. Please enter a valid video link.")
    return None


# function to get transcript from the video.
def get_transcript(video_id, language):
    ytt_api = YouTubeTranscriptApi()
    try:
        transcript = ytt_api.fetch(video_id, languages=[language])
        full_transcript = " ".join([i.text for i in transcript])
        time.sleep(10)
        return full_transcript
    except Exception as e:
        st.error(f"Error fetching video: {e}")
        return None


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0.2)


def translate_transcript(transcript):
    try:
        prompt = ChatPromptTemplate.from_template(
            """
        You are an expert translator with deep cultural and linguistic knowledge.
        I will provide you with a transcript. Your task is to translate it into English with absolute accuracy, preserving:
        - Full meaning and context (no omissions, no additions).
        - Tone and style (formal/informal, emotional/neutral as in original).
        - Nuances, idioms, and cultural expressions (adapt appropriately while keeping intent).
        - Speaker’s voice (same perspective, no rewriting into third-person).
        Do not summarize or simplify. The translation should read naturally in the target language but stay as close as possible to the original intent.

        Transcript:
        {transcript}
            """
        )
        chain = prompt | llm
        response = chain.invoke({"transcript": transcript})
        return response.content
    except Exception as e:
        st.error(f"Error translating transcript: {e}")
        return None


# function to get important topics
def get_important_topics(transcript):
    try:
        prompt = ChatPromptTemplate.from_template(
            """
        You are an assistant that extracts the 5 most important topics discussed in a video transcript or summary.

            Rules:
            - Summarize into exactly 5 major points.
            - Each point should represent a key topic or concept, not small details.
            - Keep wording concise and focused on the technical content.
            - Do not phrase them as questions or opinions.
            - Output should be a numbered list.
            - show only points that are discussed in the transcript.
            Here is the transcript:
            {transcript}
         """
        )
        chain = prompt | llm
        response = chain.invoke({"transcript": transcript})
        return response.content
    except Exception as e:
        st.error(f"Error extracting important topics: {e}")
        return None


# Function to get notes from the video
def generate_notes(transcript):
    try:
        prompt = ChatPromptTemplate.from_template(
            """You are an AI note-taker. Your task is to read the following YouTube video transcript 
                and produce well-structured, concise notes.

                ⚡ Requirements:
                - Present the output as *bulleted points*, grouped into clear sections.
                - Highlight key takeaways, important facts, and examples.
                - Use *short, clear sentences* (no long paragraphs).
                - If the transcript includes multiple themes, organize them under *subheadings*.
                - Do not add information that is not present in the transcript.

                Here is the transcript:
                {transcript}"""
        )
        chain = prompt | llm
        response = chain.invoke({"transcript": transcript})
        return response.content
    except Exception as e:
        st.error(f"Error generating notes: {e}")
        return None


# Function to create chunks
def create_chunks(transcript):
    text_splitters = RecursiveCharacterTextSplitter(
        chunk_size=10000, chunk_overlap=1000
    )
    doc = text_splitters.create_documents([transcript])
    return doc


def create_vector_store(docs):
    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vector_store = Chroma.from_documents(docs, embedding)
    return vector_store


# RAG function
def rag_answer(question, vectorstore):
    results = vectorstore.similarity_search(question, k=4)
    context_text = "\n".join([i.page_content for i in results])
    prompt = ChatPromptTemplate.from_template(
        """
                You are a kind, polite, and precise assistant.
                - Begin with a warm and respectful greeting (avoid repeating greetings every turn).
                - Understand the user’s intent even with typos or grammatical mistakes.
                - Answer ONLY using the retrieved context.
                - If answer not in context, say:
                  "I couldn’t find that information in the database. Could you please rephrase or ask something else?"
                - Keep answers clear, concise, and friendly.

                Context:
                {context}

                User Question:
                {question}

                Answer:
                """
    )
    chain = prompt | llm
    response = chain.invoke({"context": context_text, "question": question})
    return response.content


# Function to generate PDF of notes
def generate_pdf(video_title, important_topics, notes, save_path="notes"):
    """
    Generates a PDF with important topics and notes using modern fpdf2 API.

    Args:
        video_title: Title of the video
        important_topics: String containing important topics
        notes: String containing generated notes
        save_path: Directory path to save PDF (default: "notes" folder)

    Returns:
        Full path of saved PDF file or None if error
    """
    try:
        os.makedirs(save_path, exist_ok=True)
        pdf = FPDF()
        pdf.add_page()

        # Title Section
        pdf.set_font("helvetica", "B", 20)
        pdf.cell(
            0, 15, text="Video Notes", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C"
        )
        pdf.ln(5)

        # Video Title
        pdf.set_font("helvetica", "I", 12)
        pdf.multi_cell(0, 8, f"Video: {video_title}")
        pdf.ln(3)

        # Timestamp
        pdf.set_font("helvetica", "", 10)
        pdf.cell(
            0,
            6,
            f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        pdf.ln(8)

        # Divider line
        pdf.set_draw_color(33, 128, 141)
        pdf.set_line_width(0.5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)

        # Important Topics Section
        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(33, 128, 141)
        pdf.cell(0, 10, "Important Topics", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)

        pdf.set_font("helvetica", "", 11)
        pdf.set_text_color(0, 0, 0)

        topics_lines = important_topics.split("\n")
        for line in topics_lines:
            cleaned = line.strip()
            if cleaned:
                pdf.multi_cell(0, 6, cleaned)
                pdf.ln(2)

        pdf.ln(8)

        # Notes Section
        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(33, 128, 141)
        pdf.cell(0, 10, "Detailed Notes", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)

        pdf.set_font("helvetica", "", 11)
        pdf.set_text_color(0, 0, 0)

        notes_lines = notes.split("\n")
        for line in notes_lines:
            cleaned = line.strip()
            if cleaned:
                # Format headings etc if desired
                if cleaned.startswith("##"):
                    pdf.ln(4)
                    pdf.set_font("helvetica", "B", 13)
                    pdf.multi_cell(0, 7, cleaned.replace("##", "").strip())
                    pdf.set_font("helvetica", "", 11)
                    pdf.ln(2)
                elif cleaned.startswith(("*", "-", "•")):
                    pdf.multi_cell(0, 6, "  " + cleaned)
                else:
                    pdf.multi_cell(0, 6, cleaned)
                pdf.ln(1)

        # Footer
        pdf.ln(10)
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.3)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)
        pdf.set_font("helvetica", "I", 9)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(
            0,
            6,
            "Generated by VidSynth AI - YouTube Content Synthesizer",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="C",
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(
            c for c in video_title if c.isalnum() or c in (" ", "-", "_")
        ).strip()
        safe_title = safe_title[:50]  # limit filename
        filename = f"{safe_title}_{timestamp}.pdf"
        full_path = os.path.join(save_path, filename)

        pdf.output(full_path)
        st.success(f"PDF successfully saved at {full_path}")
        return full_path

    except Exception as e:
        st.error(f"Error generating PDF: {e}")
        return None
