ARG BASE_PATH="/pf"

FROM node:lts as js_build
COPY package.json /src/package.json
WORKDIR /src/
RUN npm install
COPY . /src/
ARG BASE_PATH
RUN make install BASE_PATH=$BASE_PATH


FROM python:3-alpine as py_srv
COPY requirements.txt /src/requirements.txt
WORKDIR /src/
RUN pip install -r requirements.txt
COPY . /src/
COPY --from=js_build /src/static/dist /src/static/dist
ARG BASE_PATH
ENV SCRIPT_NAME=$BASE_PATH
ENTRYPOINT [ "gunicorn", "-b", "0.0.0.0:8080", "server:app" ]
