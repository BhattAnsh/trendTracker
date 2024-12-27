# Start from Python 3.9 slim image - this gives us both Python and a Debian-based system
FROM python:3.9-slim

# Set environment variables for better Docker behavior
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create Chrome installation directory early to ensure it exists
RUN mkdir -p /opt/chrome

# Combine all system updates, installations, and Chrome setup into a single RUN
# to minimize Docker layers and reduce final image size
RUN apt-get update -qq -y && \
    apt-get install -y \
        libasound2 \
        libatk-bridge2.0-0 \
        libgtk-4-1 \
        libnss3 \
        xdg-utils \
        wget \
        unzip && \
    # Download and set up Chrome
    wget -q -O chrome-linux64.zip https://bit.ly/chrome-linux64-121-0-6167-85 && \
    unzip chrome-linux64.zip && \
    rm chrome-linux64.zip && \
    mv chrome-linux64 /opt/chrome/ && \
    ln -s /opt/chrome/chrome /usr/local/bin/ && \
    # Download and set up ChromeDriver
    wget -q -O chromedriver-linux64.zip https://bit.ly/chromedriver-linux64-121-0-6167-85 && \
    unzip -j chromedriver-linux64.zip chromedriver-linux64/chromedriver && \
    rm chromedriver-linux64.zip && \
    mv chromedriver /usr/local/bin/ && \
    # Clean up to reduce image size
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set up the working directory for the application
WORKDIR /app

RUN mkdir -p static

# Install Python dependencies
# We copy requirements first to leverage Docker's cache layer system
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
# This is done last to ensure code changes don't invalidate previous layers
COPY . .

# Command to run the application using uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]