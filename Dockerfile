FROM grahamdumpleton/mod-wsgi-docker:python-3.4

WORKDIR /app

RUN pip install Flask
RUN pip install eve
RUN pip install requests

COPY . /app

RUN mod_wsgi-docker-build

EXPOSE 80
ENTRYPOINT [ "mod_wsgi-docker-start" ]

CMD [ "--working-directory", "main_server", \
      "--url-alias", "/main_server/static", "static", \
      "main_server.wsgi" ]
