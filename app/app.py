from flask import Flask, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)

REQUEST_COUNT = Counter(
    'flask_request_count',
    'Total HTTP request count',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'flask_request_latency_seconds',
    'HTTP request latency',
    ['endpoint']
)

@app.before_request
def start_timer():
    from flask import g
    g.start = time.time()

@app.after_request
def record_metrics(response):
    from flask import g, request
    latency = time.time() - g.start
    REQUEST_LATENCY.labels(endpoint=request.path).observe(latency)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()
    return response

@app.route('/')
def index():
    return 'Hello from monitored Flask!'

@app.route('/slow')
def slow():
    time.sleep(0.5)
    return 'This was slow.'

@app.route('/error')
def error():
    return 'Something went wrong.', 500

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)