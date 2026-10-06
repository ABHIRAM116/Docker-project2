from flask import Flask
import redis
import os

app = Flask(__name__)

redis_host = os.getenv("REDIS_HOST", "redis")

r = redis.Redis(
    host=redis_host,
    port=6379,
    decode_responses=True
)

@app.route("/")
def home():
    count = r.incr("visits")

    return f"""
    <h1>Docker Multi-Container App 🚀</h1>
    <p>Visitor count: {count}</p>
    <p>Flask is connected to Redis!</p>
    """

app.run(host="0.0.0.0", port=5000)
