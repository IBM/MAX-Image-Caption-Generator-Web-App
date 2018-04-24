FROM  python:alpine

COPY . /app
WORKDIR /app
RUN pip install requests tornado

EXPOSE 8088
CMD python app.py
