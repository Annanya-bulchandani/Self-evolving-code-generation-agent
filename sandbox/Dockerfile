# sandbox/Dockerfile
#this dockerfile build a container image that runs python script (runner.py) in an isolated environment
# We use a slim version of the official Python image for a smaller footprint
# 
FROM python:3.11-slim 
# We use a slim version of the official Python image for a smaller footprint

# Create and switch to non-root user for safety
RUN useradd -m sandboxuser
USER sandboxuser

# Set working directory
WORKDIR /home/sandboxuser

# Copy runner file into container
COPY runner.py .

# Default command will run runner.py
ENTRYPOINT ["python", "runner.py"]
