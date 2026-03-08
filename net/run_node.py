import configparser

# Get port from config
config = configparser.ConfigParser()
config.read("net_configs.ini")
PORT = config["network"]["port"]