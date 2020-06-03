import sys

if sys.version_info[0] == 3:
    text_type = str
    string_types = text_type,
else:
    string_types = basestring,
    text_type = unicode

try:
    # Python 3
    from collections.abc import Mapping
except ImportError:
    # Python 2
    from collections import Mapping

try:
    from simplejson import json
except ImportError:
    import json
