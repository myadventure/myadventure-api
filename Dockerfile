FROM ubuntu:20.04

# no tty
ENV DEBIAN_FRONTEND noninteractive

# get up to date
RUN apt-get update --fix-missing

# global installs [applies to all envs!]
RUN apt-get install -y build-essential git
RUN apt-get install -y python3 python3-dev python3-setuptools
RUN apt-get install -y python3-pip python3-venv
RUN apt-get install -y supervisor
RUN apt-get install -y libxml2-dev libxslt1-dev zlib1g-dev

# stop supervisor service as we'll run it manually
RUN service supervisor stop

# create a virtual environment and install all dependencies from pypi
RUN python3 -m venv /opt/venv
ADD requirements.txt /opt/venv/requirements.txt
RUN /opt/venv/bin/pip install wheel
RUN /opt/venv/bin/pip install -r /opt/venv/requirements.txt

# install gunicorn
RUN /opt/venv/bin/pip3 install gunicorn

# install supervisor-stdout
RUN pip3 install git+git://github.com/coderanger/supervisor-stdout.git

# file management, everything after an ADD is uncached, so we do it as late as
# possible in the process.
ADD supervisord.conf /etc/supervisord.conf

# Bundle app source
COPY app /opt/app

# expose port(s)
EXPOSE 5000

# start supervisor to run our wsgi server
CMD supervisord -c /etc/supervisord.conf -n
