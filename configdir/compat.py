try:
    from simplejson import json
except ImportError:
    import json

try:
    import yaml
except ImportError:
    yaml = None
