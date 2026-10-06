# Docker Project 2 — Flask + Redis Multi-Container Application

## Project Overview

A multi-container Docker application running on an AWS EC2 Ubuntu server.

The Flask application handles HTTP requests and Redis stores a visitor counter.

```text
Browser
   |
EC2 :5000
   |
Flask Container :5000
   |
my-app-network
   |
Redis Container :6379
```

## Technologies

- AWS EC2
- Ubuntu
- Docker
- Python 3.12
- Flask
- Redis
- Docker Networking

## Project Structure

```text
docker-project2/
├── README.md
└── backend/
    ├── Dockerfile
    ├── app.py
    └── requirements.txt
```

## 1. requirements.txt

```text
Flask
redis
```

`Flask` provides the web framework. `redis` is the Python client used to communicate with Redis.

## 2. app.py

```python
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

    return f'''
    <h1>Docker Multi-Container App 🚀</h1>
    <p>Visitor count: {count}</p>
    <p>Flask is connected to Redis!</p>
    '''

app.run(host="0.0.0.0", port=5000)
```

### Important code

```python
redis_host = os.getenv("REDIS_HOST", "redis")
```

Reads the Redis hostname from an environment variable. The default hostname is `redis`, which is our Redis container name.

```python
count = r.incr("visits")
```

Increments the Redis key `visits` on every request.

## 3. Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir Flask redis

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
```

### Dockerfile explanation

`FROM` — starts with a lightweight Python image.

`WORKDIR /app` — sets the working directory inside the container.

`COPY requirements.txt .` — copies the dependency file into `/app`.

`RUN pip install ...` — installs Flask and the Redis Python library while building the image.

`COPY app.py .` — copies the application into the image.

`EXPOSE 5000` — documents that Flask listens on port 5000.

`CMD ["python", "app.py"]` — starts Flask when the container starts.

## 4. Build the Flask Image

From the `backend` directory:

```bash
docker build -t my-flask-backend .
```

`-t my-flask-backend` gives the image a name.

`.` means the current directory is the build context.

Check:

```bash
docker images
```

## 5. Create the Docker Network

```bash
docker network create my-app-network
```

Check:

```bash
docker network ls
```

The custom network allows the Flask and Redis containers to communicate.

## 6. Run Redis

```bash
docker run -d   --name redis   --network my-app-network   redis:latest
```

- `-d` — detached/background mode
- `--name redis` — container name
- `--network my-app-network` — connects Redis to the custom network
- `redis:latest` — Redis image

Redis does not need public port mapping because only Flask needs to access it internally.

## 7. Run Flask

```bash
docker run -d   --name flask-app   --network my-app-network   -p 5000:5000   -e REDIS_HOST=redis   my-flask-backend
```

- `--name flask-app` — container name
- `--network my-app-network` — same network as Redis
- `-p 5000:5000` — maps EC2 port 5000 to container port 5000
- `-e REDIS_HOST=redis` — tells Flask where Redis is
- `my-flask-backend` — image to run

## 8. Verify Containers

```bash
docker ps
```

Expected:

```text
flask-app
redis
```

Check Flask logs:

```bash
docker logs flask-app
```

Expected:

```text
* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:5000
```

## 9. Test Locally

```bash
curl http://localhost:5000
```

Expected:

```text
Docker Multi-Container App 🚀
Visitor count: 1
Flask is connected to Redis!
```

Run again:

```bash
curl http://localhost:5000
```

The counter should become:

```text
Visitor count: 2
```

This proves Flask is communicating with Redis.

## 10. AWS Security Group

For browser access, add an inbound rule:

```text
Type: Custom TCP
Port: 5000
Source: 0.0.0.0/0
```

For production, restrict the source instead of allowing the entire internet.

Then open:

```text
http://<EC2-PUBLIC-IP>:5000
```

Example:

```text
http://15.207.55.164:5000
```

## 11. Useful Commands

List running containers:

```bash
docker ps
```

List all containers:

```bash
docker ps -a
```

View images:

```bash
docker images
```

View Flask logs:

```bash
docker logs flask-app
```

Follow logs:

```bash
docker logs -f flask-app
```

Stop Flask:

```bash
docker stop flask-app
```

Start Flask:

```bash
docker start flask-app
```

Remove Flask:

```bash
docker rm flask-app
```

Stop/remove Redis:

```bash
docker stop redis
docker rm redis
```

List networks:

```bash
docker network ls
```

Inspect network:

```bash
docker network inspect my-app-network
```

Inspect the image command:

```bash
docker inspect my-flask-backend --format='{{json .Config.Cmd}}'
```

Expected:

```text
["python","app.py"]
```

## 12. Troubleshooting Lessons

### Flask container exits

```bash
docker ps -a
docker logs flask-app
```

Always check container logs first.

### Check Flask installation inside the image

```bash
docker run --rm my-flask-backend python -c "import flask; print('Flask is installed')"
```

### Rebuild without cache

```bash
docker build --no-cache -t my-flask-backend .
```

### Incorrect CMD error

If you see:

```text
/bin/sh: 1: [python,: not found
```

make sure the Dockerfile contains:

```dockerfile
CMD ["python", "app.py"]
```

### Flask cannot connect to Redis

Check:

```bash
docker ps
docker network inspect my-app-network
```

Both containers must be on the same network and Flask must use:

```text
REDIS_HOST=redis
```

## 13. What I Learned

1. How to containerize a Python Flask application.
2. How to create a Docker image using a Dockerfile.
3. How to install Python dependencies inside an image.
4. How to run multiple containers.
5. How custom Docker networks work.
6. How containers communicate using container names.
7. How environment variables configure containers.
8. How host-to-container port mapping works.
9. Why internal services such as Redis do not need public ports.
10. How to troubleshoot containers using `docker ps -a` and `docker logs`.

## 14. Troubleshooting Workflow

```text
Container fails
      |
      v
docker ps -a
      |
      v
docker logs <container>
      |
      v
Identify the error
      |
      v
Fix application/Dockerfile
      |
      v
Rebuild image
      |
      v
Remove old container
      |
      v
Create new container
```

## Project Outcome

Successfully deployed a Flask + Redis multi-container application on AWS EC2.

```text
Browser
   |
EC2 :5000
   |
Flask Container
   |
Docker Network
   |
Redis Container
   |
Visitor Counter
```
