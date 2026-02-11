FROM python:3.11-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
COPY ./ui /code/ui
COPY ./main.py /code/main.py
COPY ./start.sh /code/start.sh

RUN chmod +x /code/start.sh

# HF Spaces uses 7860
EXPOSE 7860

CMD ["/code/start.sh"]