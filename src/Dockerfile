# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container to /app/src
WORKDIR /app

# Copy requirements file
COPY ../requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY .. .

# Set environment variables for Google Cloud Run
ENV PORT=8080
EXPOSE 8080

# Run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "src.app:app"]