import adventure
import json

if __name__ == '__main__':
    # load configure file
    config_file = open("config/config.json", "r")
    config_obj = json.load(config_file)
    instance = adventure.default;
    instance.init(config_obj)
    instance.start()
