"""Fixtures for the Session 07 API tests. Do not edit.

incident_api.api is imported inside the fixtures, not at the top of this file, so the
service and schema tests can run before the API module exists.
"""

import pytest


@pytest.fixture
def client(clean_env, sample_exports):
    """A TestClient for an app started with the default settings and the sample exports.

    `clean_env` makes tmp_path the working folder, and `sample_exports` copies the
    exports to tmp_path/data/exports, which is the default input_dir.
    """
    from fastapi.testclient import TestClient

    from incident_api.api import create_app

    with TestClient(create_app()) as test_client:  # `with` runs the app's startup
        yield test_client
