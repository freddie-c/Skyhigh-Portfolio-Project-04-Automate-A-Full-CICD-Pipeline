import os                                                # stdlib; reads env vars injected by the K8s Deployment
import socket                                            # stdlib; gethostname() returns the pod name inside K8s
from flask import Flask, jsonify                         # app object + JSON response helper

GREETING = "Hello world! My name is Freddie C and I am a Cloud Engineer"   # required string, hoisted for tests

app = Flask(__name__)                                    # __name__ tells Flask where to resolve resources from
counter = 0                                              # per-process, in-memory; resets on restart (see flag)


@app.route("/")                                          # root route; the graded greeting endpoint
def index():                                             # view function name is arbitrary, the route is the contract
    return jsonify(                                      # jsonify sets Content-Type: application/json automatically
        message=GREETING,                                # exact required string, single source of truth
        hostname=socket.gethostname(),                   # which pod answered; proves load balancing is real
        version=os.getenv("APP_VERSION", "dev"),         # image tag from the Deployment; this is your audit trail
    )


@app.route("/api/count")                                 # carried over from Project 3, unmodified behavior
def count():                                             # increments a per-process counter and reports it
    global counter                                       # rebinding a module-level int requires `global`
    counter += 1                                         # not atomic, not shared across workers or pods
    return jsonify(hostname=socket.gethostname(), count=counter)   # same response shape as Project 3


@app.route("/health")                                    # target for both readinessProbe and livenessProbe
def health():                                            # must stay cheap: no DB, no outbound HTTP, no disk
    return jsonify(status="ok")                          # 200 means healthy; anything else and kubelet reacts


if __name__ == "__main__":                               # True only under `python app.py`, never under gunicorn
    app.run(host="0.0.0.0", port=5001, debug=False)      # local convenience only; gunicorn serves the container
