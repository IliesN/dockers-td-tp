# our base image
FROM alpine:3.21.0

# Install Python 3, pip, and system dependencies
RUN apk add --no-cache build-base libffi-dev openssl-dev py3-pip python3

# Set the working directory
WORKDIR /usr/src/app

# Create and activate a virtual environment
RUN python3 -m venv venv

# Use the virtual environment for all commands
ENV PATH="/usr/src/app/venv/bin:$PATH"

# Copy and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py ./
COPY templates/index.html ./templates/

# Expose the application port
EXPOSE 5000

# Run the application inside the virtual environment
CMD ["python", "/usr/src/app/app.py"]

