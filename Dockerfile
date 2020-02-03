FROM python:3.8-alpine

RUN apk --no-cache add python \
                       python3 \
                       build-base \
                       python-dev \
                       python3-dev \
                       # wget dependency
                       openssl \
                       # dev dependencies
                       git \
                       bash \
                       sudo \
                       py2-pip \
                       # Pillow dependencies
                       jpeg-dev \
                       zlib-dev \
                       freetype-dev \
                       lcms2-dev \
                       openjpeg-dev \
                       tiff-dev \
                       tk-dev \
                       tcl-dev \
                       harfbuzz-dev \
                       fribidi-dev \
                       # sqlite
                       sqlite \
     && rm -rf /var/cache/apk/*

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN set -ex && mkdir /app/ 

WORKDIR /app/

COPY ./src/Pipfile ./src/Pipfile.lock /app/

RUN pip3 install pipenv

COPY ./entrypoint.sh /

RUN chmod +x /entrypoint.sh

RUN pipenv --three install -d && rm /app/Pipfile /app/Pipfile.lock

ENTRYPOINT ["/entrypoint.sh"]

# CMD ["pipenv run python manage.py runserver 0.0.0.0:8000"]
CMD ["make init"]
