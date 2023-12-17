import json


def getConfig(key: str):

    with open("config.json", 'r') as f:
        config = json.load(f)

    try:
        return config[key]
    except KeyError:
        raise KeyError(f"Config {key} not found.")


def setConfig(key: str, value):

    with open("config.json", 'r') as f:
        config = json.load(f)

    try:
        config[key] = value
    except KeyError:
        raise KeyError(f"Config {key} not found.")

    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
