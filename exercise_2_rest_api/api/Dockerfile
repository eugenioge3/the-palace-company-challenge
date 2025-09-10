FROM python:3.9

WORKDIR /code

ENV PYTHONPATH=/code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code/app

# El comando que se ejecutará cuando el contenedor arranque
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]