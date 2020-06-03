import re
from types import GeneratorType

from .compat import Mapping, string_types, text_type


class Interpolator(object):
    """
    Recursively interpolate variable placeholders in strings.

    Strings can contain template place holders for other config keys. Placeholders
    are enclosed with squiggly braces (``{{PLACEHOLDER}}``).

    - Placeholders can refer to nested keys using dot (``.``)
      notation: ``{{PARENT_KEY.NESTED_KEY}}``
    - Placeholders can refer to nested list items using at (``@``)
      notation: ``{{PARENT_KEY@1}}``
    - Placeholders may only reference number or string values.
    """

    _key_regex = re.compile(r"{{(?P<key>[^\}]+)}}")

    def __init__(self, values):
        """
        Args:
            values (dict): Values that placeholders will be replaced with.
        """
        self.values = values

    def _key_segments(self, full_key):
        """
        Yields:
             tuple[str, str|int, list[str]]: Key segment prefix ("." or "@"), key
                segment value, and list of current key path segments.
        """
        key_parts = re.split(r"(\.|@)", full_key)
        # First key is for a dictionary
        yield ".", key_parts[0], [key_parts[0]]

        for i in range(1, len(key_parts), 2):
            prefix = key_parts[i]
            key = key_parts[i + 1]
            if prefix == "@":
                # Array index
                key = int(key)

            yield prefix, key, key_parts[: i + 2]

    def _get_value(self, match):
        full_key = match.groupdict()["key"]
        value = self.values
        for prefix, key, path in self._key_segments(full_key):
            try:
                value = value[key]
            except KeyError:
                raise KeyError(
                    "Could not find key `{}` at `{}`".format(key, "".join(path))
                )
            except IndexError:
                raise IndexError(
                    "Could not find index `{}` at `{}`".format(key, "".join(path))
                )

        if isinstance(value, text_type):
            # Interpolate the value in case it is a placeholder
            value = self(value)
        elif isinstance(value, (int, float)):
            value = text_type(value)
        else:
            raise TypeError(
                "`{}` does not reference a number or string value".format(full_key)
            )

        return value

    def __call__(self, value):
        """
        Interpolate a value

        Args:
             value (mixed)

        Returns:
            mixed: The interpolated value
        """
        if isinstance(value, Mapping):
            return {k: self(v) for k, v in value.items()}
        elif isinstance(value, (list, GeneratorType)):
            return [self(v) for v in value]
        elif isinstance(value, string_types):
            return self._key_regex.sub(self._get_value, value)
        return value
