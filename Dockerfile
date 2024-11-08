# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set work directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt
RUN pip install numpy
RUN command python -m nltk.downloader punkt
RUN python -m nltk.downloader vader_lexicon


# Copy project files to the container
COPY . /app/