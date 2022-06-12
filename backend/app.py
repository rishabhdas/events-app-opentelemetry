import os
import psycopg2

from typing import Union
from fastapi import FastAPI

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
    BatchSpanProcessor,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from prometheus_client import start_http_server, Counter
import uvicorn

service_name = os.environ.get('SERVICE_NAME', 'events-app-backend')
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

app = FastAPI()
FastAPIInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
tracer = trace.get_tracer(__name__)

def connect_db():
    conn = psycopg2.connect(
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "postgres"),
        dbname=os.environ.get("DB_NAME", "eventsapp"),
        host=os.environ.get("DB_HOST", "localhost")
    )
    return conn

@app.get("/api/events")
def read_events():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * from events;")
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    events = []
    for record in records:
        event = {
            "eventid": record[0],
            "eventname": record[1]
        }
        events.append(event)
    return {"events": events}

@app.get("/api/event/{eventid}")
def read_event(eventid: int):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * from events where eventid = %s", (eventid,))
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    for record in records:
        eventdetails = {
            "eventname": record[1],
            "startdate": record[2],
            "enddate": record[3]
        }
    return eventdetails

@app.get("/api/event/{eventid}/participants")
def read_participants(eventid: int):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT pname from participants where eventid = %s", (eventid,))
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    participants = []
    for record in records:
        participants.append(record[0])
    return {"participants": participants}

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("APP_PORT", 3000)))
