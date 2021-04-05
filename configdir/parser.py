import os

from urllib.parse import quote

from .exceptions import ConfigDirMissingError
from .interpolator import Interpolator
from .compat import json, yaml


def _uri_parameter_formatter(key, value, values):
    return quote(value, safe="")


def _get_config_values(directory, key_settings, parent):
    config = {}
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        key_name, ext = os.path.splitext(name)
        if key_name in config:
            raise KeyError(
                "Duplicate config key named `{}` with path {}".format(key_name, path)
            )
        if os.path.isdir(path):
            config[key_name] = _get_config_values(
                path, key_settings, parent + (key_name,)
            )
        else:
            settings = key_settings.setdefault(parent + (key_name,), {})
            with open(path, "rb") as f:
                contents = f.read().strip()

            interpolate = True
            if ext == ".json":
                contents = json.loads(contents)
            elif ext == ".bin":
                # Leave value as is
                interpolate = False
            elif ext == ".yaml":
                if not yaml:
                    raise TypeError("YAML not supported: {}".format(path))
                contents = yaml.safe_load(contents)
            elif ext == ".uri":
                settings["formatter"] = _uri_parameter_formatter
                contents = contents.decode("utf8")
            else:
                contents = contents.decode("utf8")

            if interpolate:
                settings["interpolate"] = True

            config[key_name] = contents
    return config


def parse(directory):
    """
    Parse a ConfigDir

    Args:
        directory (str): Directory path to config contents.

    Returns:
        dict: Config values

    Raises:
        ConfigDirMissingError: When configuration directory is missing.
    """
    if not os.path.isdir(directory):
        raise ConfigDirMissingError("`{}` is not a directory.".format(directory))

    key_settings = {}
    config = _get_config_values(directory, key_settings, ())
    interpolate = Interpolator(config)

    for key_names, settings in key_settings.items():
        c = config
        for k in key_names[:-1]:
            c = c[k]

        if settings.get("interpolate"):
            c[key_names[-1]] = interpolate(c[key_names[-1]], formatter=settings.get("formatter"))

    return config
