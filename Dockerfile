FROM python:3.12-bullseye

# In production we would do proper packaging and not just copy the data
COPY . /app
WORKDIR /app
# Provide 'DB_STRING' env var.

RUN ["python3", "-m", "pip", "install", "-r", "requirements.txt"]

ENTRYPOINT [ "python3", "./viboo" ]
