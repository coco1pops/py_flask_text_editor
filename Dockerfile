# Use an official Python runtime as a parent image
FROM python:3.12.1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Make port 8080 available to the world outside this image
# Flask typically runs on 5000, but Cloud Run expects 8080
ENV PORT 8080
EXPOSE 8080

# Define environment variable for the database (we'll handle this later)
# ENV DATABASE_URL="sqlite:///app/mydatabase.db" # Example, will be overridden

# Run app.py when the container launches
# Use gunicorn for production WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "editor:__init__"]