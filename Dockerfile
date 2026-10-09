FROM python:3.12-slim-bookworm

WORKDIR /usr/src/app

COPY ./requirements.txt ./

# Every compiled dependency (pandas, pillow) ships manylinux wheels for amd64 and
# arm64, so no compilers or -dev packages are needed. Security updates come from
# the base image, which the monthly rebuild pulls fresh.
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

ADD ./TwitchChannelPointsMiner ./TwitchChannelPointsMiner
ENTRYPOINT [ "python", "run.py" ]
