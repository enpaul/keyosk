import os
from pathlib import Path

import toml

from keyosk import config
from keyosk import constants
from keyosk import datatypes


TEST_CONFIG = {
    "storage": {
        "backend": "maria",
        "sqlite": {
            "path": "/foo/bar/baz.db",
            "pragmas": {"foo": 1, "bar": "buzz", "baz": ["dog", "cat"]},
        },
        "maria": {
            "schema": "authentifiy",
            "host": "10.20.30.40",
            "port": 6033,
            "username": "qwerty",
            "password": "uiop",
        },
    }
}


def test_default():
    assert config.load() == config.KeyoskConfig()


def test_roundtrip():
    serializer = config.ConfigSerializer()
    loaded = serializer.load(TEST_CONFIG)
    assert TEST_CONFIG == serializer.dump(loaded)
    assert loaded == serializer.load(serializer.dump(loaded))


def test_settings():
    loaded = config.ConfigSerializer().load(TEST_CONFIG)
    assert loaded.storage.backend == datatypes.StorageBackend.MARIA
    assert loaded.storage.sqlite.path == Path(TEST_CONFIG["storage"]["sqlite"]["path"])
    assert loaded.storage.sqlite.pragmas == TEST_CONFIG["storage"]["sqlite"]["pragmas"]
    for key, value in TEST_CONFIG["storage"]["maria"].items():
        assert getattr(loaded.storage.maria, key) == value


def test_filepath(tmp_path):
    tmp_file = Path(tmp_path, "conf.toml")
    os.environ[constants.ENV_CONFIG_PATH] = str(tmp_file)
    with tmp_file.open("w+") as outfile:
        toml.dump(TEST_CONFIG, outfile)

    assert config.load(tmp_file) == config.ConfigSerializer().load(TEST_CONFIG)
    tmp_file.unlink()
    assert config.load(tmp_file) == config.KeyoskConfig()