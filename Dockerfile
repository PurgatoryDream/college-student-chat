# Start from a base Python 3.9 image
FROM python:3.9

# Set a working directory
WORKDIR /app

# Copy requirements.txt and install the Python dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the application code
COPY ./code /app

# Expose port 5000 for the Flask app to listen on
EXPOSE 5000

CMD [ "python", "./main.py" ]