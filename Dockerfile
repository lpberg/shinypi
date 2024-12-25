# Use the appropriate Python base image
FROM python:3.9-slim-buster

# Copy Requirements file
COPY requirements.txt /app/requirements.txt

# Set the working directory in the container
WORKDIR /app

# Install necessary packages
RUN pip install -r requirements.txt

# Copy the application files to the container
COPY app.py .
COPY read_data_from_file.py .

# Expose the port that Shiny will run on
EXPOSE 8888

# Command to run when the container starts
CMD ["shiny", "run", "--host", "0.0.0.0", "--port", "8888", "app.py"]
