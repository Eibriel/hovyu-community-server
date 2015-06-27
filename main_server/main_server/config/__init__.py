from main_server.config.country_argentina import argentina

try:
    from main_server.config.local import Local as Config
except :
    from main_server.config.default import Config
