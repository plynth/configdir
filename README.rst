=========
ConfigDir
=========

File names for keys. File contents for values.

For security, simplicity, and consistency, all configuration is in files |--|
not environmental variables.

.. contents:: :local:


Features
--------

- Security |--| Environmental variables set on a Docker image or container are
  injectable outside the container. This means environmental variables are
  insecure for secrets like passwords or encryption keys.
- Simplicity |--| ConfigDir is simple to parse. This makes it easy for any
  language to parse. It is particularly useful for shell interpreters like
  bash.
- Consistency |--| Rather than have two or more ways to configure an
  application securely (files for secrets, environmental variables for
  everything else), all configuration is done as files.
- Kubernetes Integration |--| Easy to generate from ConfigMaps_ or Secrets_
- Variable Interpolation |--| Configuration values can reference other
  configuration values. Kubernetes only interpolates variables for
  ``command``, ``args``, or ``env`` fields so Kubernetes variable
  interpolation can not be used when volume mounting ConfigMaps_ or
  Secrets_ as files.


ConfigDir Standard
------------------

Configuration is mounted as a directory of files in ``/configdir``
(by default). The configuration directory can be overridden with the
environmental variable ``CONFIGDIR``.

Each key is create as a file named ``/configdir/{key}``. The configuration,
when parsed, will be a dictionary where the keys of the dictionary are
the child file names.

Nested keys are allowed: ``/configdir/{key}/{sub-key}``. If the parent key
is a directory, the value will be a dictionary where the keys of the
dictionary are the child file names. There is no limit to directory nesting
depth.


Filenames
~~~~~~~~~

Each filename consists of up to two parts: the ``name`` and an optional
``extension``. Only the ``name`` portion is used for the configuration key.

- ``name`` must consist solely of lowercase ascii letters, uppercase ascii
  letters, digits, and underscore and must not begin with a digit
  (``[a-zA-Z_][a-zA-Z0-9_]*``).
- ``extension`` must be omitted or be one of the `File Types`_ below.


File Contents
~~~~~~~~~~~~~

Trailing and leading whitespace is removed from file contents (except for
``.bin`` files).


Variable Interpolation
++++++++++++++++++++++

Files can contain template place holders for other config keys. Placeholders
are enclosed with squiggly braces (``{{PLACEHOLDER}}``).

- Placeholders can refer to nested keys using dot (``.``)
  notation: ``{{PARENT_KEY.NESTED_KEY}}``
- Placeholders can refer to nested list items using at (``@``)
  notation: ``{{PARENT_KEY@1}}``
- Placeholders may only reference number or string values.

File Types
++++++++++

- A File with no extension has a value that is UTF-8 encoded and can
  contain interpolated variables.
- ``.json`` will automatically be decoded as JSON then each value will be
  interpolated.
- ``.yaml`` will automatically be decoded as YAML then each value will be
  interpolated.
- ``.bin`` will not be UTF8 decoded, will not be interpolated, and will be
  loaded as binary.


Example
~~~~~~~


Directory Contents
++++++++++++++++++

=================================================================  ========
File Path                                                          Contents
=================================================================  ========
``/configdir/REDIS_URI``                                           ``redis://:{{REDIS_PASSWORD}}@{{REDIS_HOST}}:{{REDIS_PORT}}/{{REDIS_SENTINEL_MASTER}}/0``
``/configdir/REDIS_PASSWORD``                                      ``$3cr3t``
``/configdir/REDIS_SENTINEL_MASTER``                               ``mymaster``
``/configdir/REDIS_HOST``                                          ``redis-sentinel``
``/configdir/REDIS_PORT``                                          ``6319``
``/configdir/CELERY_BROKER_URL``                                   ``sentinel://{{REDIS_HOST}}:{{REDIS_PORT}}``
``/configdir/CELERY_BROKER_TRANSPORT_OPTIONS/master_name``         ``{{REDIS_SENTINEL_MASTER}}``
``/configdir/CELERY_BROKER_TRANSPORT_OPTIONS/visibility_timeout``  ``3600``
``/configdir/POSTGRES_DB_URI``                                     ``postgresql://root:postgres@postgres:5432/database``
``/configdir/SMTP/username``                                       ``sender``
``/configdir/SMTP/password``                                       ``$3cr3t``
``/configdir/SMTP/port``                                           ``542``
``/configdir/SMTP/host``                                           ``mail.mailgun.com``
``/configdir/SMTP/certificate.bin``	                               ``<binary>``
``/configdir/KEYS.json``                                           ``{"keys": {"id": 1, "private_key": "<pem>"}}``
``/configdir/PUBLIC_KEY.bin``	                                     ``<binary>``
=================================================================  ========


Parsed ConfigDir
++++++++++++++++

.. code-block:: json

  {
    "PUBLIC_KEY": "<binary>",
    "KEYS": {
      "keys": {
        "id": 1,
        "private_key": "<pem>"
      }
    },
    "CELERY_BROKER_TRANSPORT_OPTIONS": {
      "master_name": "mymaster",
      "visibility_timeout": "3600"
    },
    "CELERY_BROKER_URL": "sentinel://redis-sentinel:6319",
    "POSTGRES_DB_URI": "postgresql://root:postgres@postgres:5432/database",
    "REDIS_HOST": "redis-sentinel",
    "REDIS_PASSWORD": "$3cr3t",
    "REDIS_PORT": "6319",
    "REDIS_SENTINEL_MASTER": "mymaster",
    "REDIS_URI": "redis://:$3cr3t@redis-sentinel:6319/mymaster/0",
    "SMTP": {
      "certificate": "<binary>",
      "host": "mail.mailgun.com",
      "password": "$3cr3t",
      "port": "542"
    }
  }


Python Usage
------------

.. code-block:: python

  from configdir import configdir
  config = configdir()
  print(config["REDIS_URI"])


Similar Projects
----------------

- `envdir <http://cr.yp.to/daemontools/envdir.html>`_ |--| Launches a
  sub-process with configuration directory contents as environmental
  variables. There is also a `Python port <https://github.com/jezdez/envdir>`_.
- `confdir <https://github.com/misli/python-confdir>`_ |--| Python
  based.

.. _ConfigMaps: https://kubernetes.io/docs/concepts/configuration/configmap/
.. _Secrets: https://kubernetes.io/docs/concepts/configuration/secret/
.. |--| unicode:: U+2013   .. en dash