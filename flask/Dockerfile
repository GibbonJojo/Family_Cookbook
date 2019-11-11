# Load Container -> Python 3.7.3
FROM python:3.7-stretch
# Set working directory
WORKDIR /app
# Copy contents into container
ADD . /app
# Install dependencies
RUN pip install -r requirements.txt

EXPOSE 8080

# start WSGI
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]