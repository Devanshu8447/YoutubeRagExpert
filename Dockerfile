# Use a Python base image suitable for Streamlit
FROM python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PORT 8501
# Set the Streamlit port/address for the CMD
ENV STREAMLIT_SERVER_PORT 8501
ENV STREAMLIT_SERVER_ADDRESS 0.0.0.0

# Set the working directory in the container
WORKDIR /app

# --- Dependencies ---
# Copy requirements.txt first to leverage Docker layer caching
COPY requirements.txt .

# Install the heavy hitters first (like sentence-transformers)
RUN pip install --no-cache-dir sentence-transformers transformers

# Install core app dependencies
RUN pip install --no-cache-dir streamlit langchain langchain-community python-dotenv fpdf2

# Install Google/Chroma dependencies
RUN pip install --no-cache-dir langchain-google-genai langchain-chroma google-genai

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# --- Application Code ---
# Copy the core application files
COPY app.py .
COPY supporting_functions.py .

# Create the 'notes' directory used by generate_pdf (if not present in build context)
# The generate_pdf function creates this folder if it doesn't exist, but it's good practice
# to ensure the container has permissions to write to it.
RUN mkdir -p notes

# --- Environment Setup (for API Key) ---
# IMPORTANT: Use AWS Secrets Manager or ECS Task Definition to inject GOOGLE_API_KEY
# Do NOT store the actual key here. This line just shows where it will be used.
# If you rely on .env, you must load it in supporting_functions, but it's better to pass it directly.
# The 'supporting_functions.py' loads the environment, so we'll ensure the variable is set externally.

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]