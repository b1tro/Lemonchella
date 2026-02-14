FROM python:3.12

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

COPY . /app
CMD ["python", "run.py"]