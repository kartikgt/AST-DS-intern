import pytest
import os
import shutil
from src.utils import load_config

TMP_CONFIG_DIR = "tests/tmp_config"
TMP_CONFIG_PATH = TMP_CONFIG_DIR + "/tmp_config.yaml"

def setup_module():
    os.makedirs(TMP_CONFIG_DIR, exist_ok=True)
    with open(TMP_CONFIG_PATH, "w") as f:
        f.write("test_key: test_value")
    return None

def teardown_module():
    shutil.rmtree(TMP_CONFIG_DIR)

@pytest.fixture
def config():
    return load_config(TMP_CONFIG_PATH)


def test_config(config):
    assert config == {"test_key" : "test_value"}
