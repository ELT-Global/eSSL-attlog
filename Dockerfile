# Use the official Python image
FROM python:3.14.0-trixie

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file first to leverage Docker cache
COPY ./requirements.txt /code/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the app directory
COPY ./app /code/app

# Copy the main.py file
COPY ./main.py /code/

# Create data directory and set it as volume
RUN mkdir -p /code/data
VOLUME ["/code/data"]

# Expose port 80
EXPOSE 80

# Run the FastAPI application with Uvicorn
CMD ["fastapi", "run", "main.py", "--port", "80"]