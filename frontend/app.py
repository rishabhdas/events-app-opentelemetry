import os
import requests
import json
from flask import Flask, render_template

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
    BatchSpanProcessor,
)
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from prometheus_client import start_http_server, Counter

service_name = os.environ.get('SERVICE_NAME', 'events-app-frontend')
agent_host = os.environ.get('AGENT_HOST', 'localhost')
agent_port = os.environ.get('AGENT_PORT', '6831')

trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: service_name})
    )
)

jaeger_exporter = JaegerExporter(
    agent_host_name = agent_host,
    agent_port = int(agent_port),
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Create a metric to track total number of requests made.
REQUEST_TOTAL = Counter('total_requests', 'Total number of HTTP requests')


app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
tracer = trace.get_tracer(__name__)

@app.route("/")
def index():
    REQUEST_TOTAL.inc()
    return render_template("index.html")

@app.route("/events")
def get_events():
    REQUEST_TOTAL.inc()
    # with tracer.start_as_current_span("/ events"):
    # with tracer.start_as_current_span("/ api/events"):
    #     events = requests.get("{}/api/events".format(API_HOST_URL))
    events = requests.get("{}/api/events".format(API_HOST_URL))
    print(events.json())
    return render_template("events.html", events=events.json(), hostname=UI_HOST_URL)


@app.route("/event/<eventid>")
def get_event_details(eventid):
    REQUEST_TOTAL.inc()
    with tracer.start_as_current_span("/ api/event/{}".format(eventid)):
        eventdetails = requests.get("{}/api/event/{}".format(API_HOST_URL, eventid))
    with tracer.start_as_current_span("/ api/event/{}/participants".format(eventid)):
        participants = requests.get("{}/api/event/{}/participants".format(API_HOST_URL, eventid))
    # eventdetails = requests.get("{}/api/event/{}".format(API_HOST_URL, eventid))
    # participants = requests.get("{}/api/event/{}/participants".format(API_HOST_URL, eventid))
    return render_template("event-details.html", event=eventdetails.json(), participants=participants.json())

if __name__=="__main__":
    API_HOST_URL = os.environ.get("API_HOST_URL", "http://localhost:3000")
    UI_HOST_URL = os.environ.get("UI_HOST_URL", "http://localhost:8000")
    app.run(host="0.0.0.0", port=8000, debug=True)