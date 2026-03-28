FROM python:3.10-slim

WORKDIR /app

# Install dependencies first (better Docker layer caching).
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the project.
COPY . /app

# Run the project entrypoint.
CMD ["python", "run_agent.py"]

