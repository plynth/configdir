import os

from .exceptions import ConfigDirMissingError
from .interpolator import Interpolator
from .compat import json, yaml


def _get_config_values(directory, interpolate_keys, parent):
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
                path, interpolate_keys, parent + (key_name,)
            )
        else:
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
            else:
                contents = contents.decode("utf8")

            if interpolate:
                interpolate_keys.add(parent + (key_name,))

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

    interpolate_keys = set()
    config = _get_config_values(directory, interpolate_keys, ())
    interpolate = Interpolator(config)

    for key_names in interpolate_keys:
        c = config
        for k in key_names[:-1]:
            c = c[k]

        c[key_names[-1]] = interpolate(c[key_names[-1]])

    return config
