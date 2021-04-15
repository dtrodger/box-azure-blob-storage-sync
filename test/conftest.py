import os
import yaml

import pytest


TEST_CONFIG_FILE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "env", f"test.yml"
)


@pytest.fixture(scope="session")
def config_dict():
    with open(TEST_CONFIG_FILE_PATH) as config_fh:
        return yaml.load(config_fh, Loader=yaml.FullLoader)
