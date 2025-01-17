# Dockerized phonebook app for Ops School project
FROM python:3.6
LABEL Maintainer = Shashank

# Create app directory
WORKDIR /app

# Install app dependencies
COPY src/requirements.txt ./
RUN pip3 install -r requirements.txt

# Bundle app source
COPY src /app

EXPOSE 8000
CMD ["python","myPhonebook.py"]