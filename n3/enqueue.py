from flask import Flask, redirect, request
from waitress import serve
import redis
import json
from rq import Queue
import tasks

app = Flask(__name__)

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
q = Queue(connection=redis_client)

@app.route('/', methods=['POST'])
def enqueue_task():
    job = request.json
    print(job)
    q.enqueue(tasks.run_spider, job)
    return {"status": "success"}, 202


serve(app, host="0.0.0.0", port=8080)