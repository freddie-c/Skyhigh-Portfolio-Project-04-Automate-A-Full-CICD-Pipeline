import pytest                                            # test framework; supplies the fixture decorator
from app import app as flask_app, GREETING               # import the real app object and the required string


@pytest.fixture                                          # a fixture is reusable setup, injected by parameter name
def client():                                            # any test declaring a `client` arg receives this object
    flask_app.config.update(TESTING=True)                # surfaces real exceptions instead of generic 500 pages
    with flask_app.test_client() as c:                   # test_client dispatches requests with no socket, no port
        yield c                                          # hand the client to the test; cleanup resumes after


def test_root_returns_greeting(client):                  # the required passing test
    resp = client.get("/")                               # simulated GET /; no container, no network, milliseconds
    assert resp.status_code == 200                       # gate 1: route exists and the view didn't raise
    assert resp.get_json()["message"] == GREETING        # gate 2: exact string, not a close-enough lookalike


def test_health_returns_ok(client):                      # probes are a contract; test them like any endpoint
    resp = client.get("/health")                         # if this breaks, K8s restarts healthy pods forever
    assert resp.status_code == 200                       # kubelet only accepts 2xx as healthy
    assert resp.get_json()["status"] == "ok"             # shape matters too, not just the status code


def test_count_increments(client):                       # behavioral test: state actually changes between calls
    first = client.get("/api/count").get_json()["count"]     # capture the counter value
    second = client.get("/api/count").get_json()["count"]    # call again in the same process
    assert second == first + 1                           # exactly one increment, no double-counting


def test_unknown_route_404(client):                      # negative test: prove the app rejects what it should
    assert client.get("/nope").status_code == 404        # a catch-all route would silently break this
