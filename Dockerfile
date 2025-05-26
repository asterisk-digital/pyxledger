FROM python:3.11-slim

# Install uv (fast installer for Python projects)
RUN pip install uv

# Set the working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml /app/
COPY src/ /app/

# Install dependencies using uv
RUN uv pip install .

# Run the application
CMD ["python", "main.py"]
