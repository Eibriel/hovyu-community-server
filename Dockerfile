FROM grahamdumpleton/mod-wsgi-docker:python-3.4

WORKDIR /app

RUN pip install babel

COPY . /app

RUN pybabel compile -d main_server/main_server/translations

RUN mod_wsgi-docker-build

EXPOSE 80
ENTRYPOINT [ "mod_wsgi-docker-start" ]

CMD [ "--working-directory", "main_server", \
      "--url-alias", "/main_server/static", "static", \
      "main_server.wsgi" ]
