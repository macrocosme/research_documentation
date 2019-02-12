# docker run -it -p 8888:8888 -v [YOUR_FOLDER]:/home/jovyan/work sm-python-bi start-notebook.sh --NotebookApp.token='[YOUR_PASSWORD]'
FROM jupyter/scipy-notebook

WORKDIR /code
ADD requirements.txt /code/

USER root
RUN apt-get update
RUN apt-get install -y apt-utils python-dev python3-dev libmysqlclient-dev

USER jovyan
WORKDIR /home/jovyan/work
ADD . /home/jovyan/work
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
