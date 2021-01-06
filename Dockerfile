FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN pip install pipenv
COPY Pipfile* /app/
RUN pipenv install
COPY . /app/
