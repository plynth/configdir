# coding=utf-8
from __future__ import unicode_literals

import os

import pytest

from configdir import configdir
from configdir.exceptions import ConfigDirMissingError
from configdir.interpolator import Interpolator

_SAMPLE_FILES = """\
REDIS_URI.uri: redis://:{{REDIS_PASSWORD}}@{{REDIS_HOST}}:{{REDIS_PORT}}/{{REDIS_SENTINEL_MASTER}}/0
REDIS_PASSWORD: $3cr3t
REDIS_SENTINEL_MASTER: mymaster
REDIS_HOST: redis-sentinel
REDIS_PORT: 6319
UNICODE: ∫å∂¬∑π∑
CELERY_BROKER_URL.uri: sentinel://{{REDIS_HOST}}:{{REDIS_PORT}}
CELERY_BROKER_TRANSPORT_OPTIONS/master_name: {{REDIS_SENTINEL_MASTER}}
CELERY_BROKER_TRANSPORT_OPTIONS/visibility_timeout: 3600
POSTGRES_DB_URI.uri: postgresql://root:postgres@postgres:5432/database
SMTP/username: sender
SMTP/password: $3cr3t
SMTP/port: 542
SMTP/host: mail.mailgun.com
SMTP/certificate.bin: <binary certificate>
KEYS.json: {"keys": [{"id": 1, "private_key": "<private key pem>"}]}
PUBLIC_KEY.bin: <public key binary>
FIRST_PRIVATE_KEY: {{KEYS.keys@0.private_key}}
INTERPOLATED_JSON.json: {"redis": "{{REDIS_URI}}", "redis_master": ["{{REDIS_SENTINEL_MASTER}}"]}
INTERPOLATED_YAML.yaml: redis: '{{REDIS_URI}}'
BLOBSTORE_URI.uri: http://{{BLOBSTORE_ACCESS_KEY}}:{{BLOBSTORE_SECRET_KEY}}@blobstore/
BLOBSTORE_ACCESS_KEY: aderattsrngmvoc1gogj54
BLOBSTORE_SECRET_KEY: C/Ahz+pAA/NMWirgEy4Pg==
"""


@pytest.fixture
def sample_config_dir(tmpdir):
    """
    Sample ConfigDir files

    Returns:
         Path: Path to ConfigDir
    """
    directory = tmpdir.join("configdir").ensure(dir=True)
    for line in _SAMPLE_FILES.splitlines(False):
        if line.strip():
            filename, c = line.strip().split(":", 1)
            path = directory.join(filename.strip())
            path.write(c.strip().encode("utf8"), mode="wb", ensure=True)
    return directory


def test_config_dir(sample_config_dir):
    """
    Verify ConfigDir can be loaded
    """
    values = configdir(str(sample_config_dir))
    assert values == {
        "CELERY_BROKER_TRANSPORT_OPTIONS": {
            "master_name": "mymaster",
            "visibility_timeout": "3600",
        },
        "CELERY_BROKER_URL": "sentinel://redis-sentinel:6319",
        "FIRST_PRIVATE_KEY": "<private key pem>",
        "INTERPOLATED_JSON": {
            "redis": "redis://:$3cr3t@redis-sentinel:6319/mymaster/0",
            "redis_master": ["mymaster"],
        },
        "INTERPOLATED_YAML": {
            "redis": "redis://:$3cr3t@redis-sentinel:6319/mymaster/0"
        },
        "KEYS": {"keys": [{"id": 1, "private_key": "<private key pem>"}]},
        "POSTGRES_DB_URI": "postgresql://root:postgres@postgres:5432/database",
        "PUBLIC_KEY": b"<public key binary>",
        "REDIS_HOST": "redis-sentinel",
        "REDIS_PASSWORD": "$3cr3t",
        "REDIS_PORT": "6319",
        "REDIS_SENTINEL_MASTER": "mymaster",
        "REDIS_URI": "redis://:%243cr3t@redis-sentinel:6319/mymaster/0",
        "SMTP": {
            "certificate": b"<binary certificate>",
            "host": "mail.mailgun.com",
            "password": "$3cr3t",
            "port": "542",
            "username": "sender",
        },
        "UNICODE": "∫å∂¬∑π∑",
        "BLOBSTORE_URI": "http://aderattsrngmvoc1gogj54:C%2FAhz%2BpAA%2FNMWirgEy4Pg%3D%3D@blobstore/",
        "BLOBSTORE_ACCESS_KEY": "aderattsrngmvoc1gogj54",
        "BLOBSTORE_SECRET_KEY": "C/Ahz+pAA/NMWirgEy4Pg=="
    }


def test_variable_interpolation():
    """
    Verify variable interpolation placeholders are replaced with the referenced value.
    """
    values = {
        "UNICODE": "∫å∂¬∑π∑",
        "SMTP": {
            "certificate": b"<binary>",
            "host": "mail.mailgun.com",
            "password": "$3cr3t",
            "port": "542",
            "username": "sender",
        },
        "KEYS": {"keys": [{"id": 1, "private_key": "<private key pem>"}]},
        "other_settings": {
            "host": "{{SMTP.host}}",
            "user_and_password": ["{{SMTP.username}}", "{{SMTP.password}}"],
        },
    }
    interpolate = Interpolator(values)

    assert interpolate("{{UNICODE}}") == "∫å∂¬∑π∑"
    assert interpolate("{{SMTP.host}}") == "mail.mailgun.com"
    assert interpolate("{{KEYS.keys@0.private_key}}") == "<private key pem>"

    # Referencing an integer is OK, but it comes out as a string
    assert interpolate("{{KEYS.keys@0.id}}") == "1"

    # Can not reference binary
    with pytest.raises(TypeError):
        interpolate("{{SMTP.certificate}}")
    # Can not reference a dictionary
    with pytest.raises(TypeError):
        interpolate("{{KEYS}}")
    # Can not reference a list
    with pytest.raises(TypeError):
        interpolate("{{KEYS.keys}}")
    # Invalid list index
    with pytest.raises(IndexError):
        interpolate("{{KEYS.keys@1.private_key}}")
    # Invalid dictionary key
    with pytest.raises(KeyError):
        interpolate("{{KEYS.not_a_key@0.private_key}}")


def test_config_dir_directory(monkeypatch):
    """
    Verify `configdir` directory:

    - Defaults to /configdir
    - Can be overridden with env var
    """
    def _just_return_dir(directory):
        return directory
    monkeypatch.setattr("configdir.parse", _just_return_dir)

    assert configdir() == "/configdir"
    assert configdir("/foo") == "/foo"

    monkeypatch.setitem(os.environ, "CONFIGDIR", "/bar")
    assert configdir() == "/bar"


def test_directory_error():
    """
    Verify exception raised if config directory does not exist
    """
    with pytest.raises(ConfigDirMissingError):
        configdir("/not/a/directory")
