FROM python:3.12.8-slim

WORKDIR /app

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080
ENV FLASK_ENV=development

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 8080

COPY . .

CMD ["flask", "run", "--debug"]