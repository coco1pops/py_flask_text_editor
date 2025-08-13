# Use an official Python runtime as a parent image
FROM python:3.12.1

# Set the working directory in the container
WORKDIR /app

RUN pip install --no-cache-dir psycopg2-binary

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# --- IMPORTANT PART FOR ENVIRONMENT VARIABLES ---
# Define build arguments for your database credentials
ARG FLASK_DB_USER
ARG FLASK_DB_PASSWORD
ARG FLASK_DB_HOST
ARG FLASK_DB_NAME
ARG FLASK_DB_PORT
ARG ENVIRONMENT
ARG CLOUD_SQL_CONNECTION_NAME

# Set these build arguments as environment variables within the image
ENV FLASK_DB_USER=${FLASK_DB_USER}
ENV FLASK_DB_PASSWORD=${FLASK_DB_PASSWORD}
ENV FLASK_DB_HOST=${FLASK_DB_HOST}
ENV FLASK_DB_NAME=${FLASK_DB_NAME}
ENV FLASK_DB_PORT=$(FLASK_DB_PORT)
ENV ENVIRONMENT=$(ENVIRONMENT)
ENV CLOUD_SQL_CONNECTION_NAME=$(CLOUD_SQL_CONNECTION_NAME)
# -------------------------------------------------

# Make port 8080 available to the world outside this image
# Flask typically runs on 5000, but Cloud Run expects 8080
EXPOSE 8080

# Run app.py when the container launches
# Use gunicorn for production WSGI server
CMD gunicorn editor:app --bind 0.0.0.0:$PORT --log-level debug
