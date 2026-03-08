# Use a professional AI-focused base image
FROM python:3.10-slim

# 1. INSTALL SYSTEM LIBRARIES (Crucial for AI/Image processing)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# 2. SET UP THE WORKSPACE
WORKDIR /app

# 3. INSTALL AI DEPENDENCIES
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. DEPLOY THE ENGINE
COPY . .

# 5. CONFIGURE FOLDERS
RUN mkdir -p inputs outputs && chmod -R 777 inputs outputs

# 6. EXPOSE THE CLOUD PORT (Hugging Face default)
EXPOSE 7860

# 7. LAUNCH THE BRAIN
CMD ["python", "server.py"]
