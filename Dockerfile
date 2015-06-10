FROM grahamdumpleton/mod-wsgi-docker:python-3.4-onbuild

CMD [ "--working-directory", "main_server", \
      "--url-alias", "/main_server/static", "static", \
      "main_server.wsgi" ]
