FROM python:3.8
LABEL maintainer="Alan Brant"

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

# initialize the database
RUN python init_db.py

# command to run on container start
CMD [ "python", "app.py" ]

EXPOSE 3111