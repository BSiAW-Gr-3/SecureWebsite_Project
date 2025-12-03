FROM python:3.11-slim

# Create a non-root user
RUN groupadd -g 1001 appgroup && \
    useradd -r -u 1001 -g appgroup appuser

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appgroup . /app 

# Install dependencies as root
RUN pip install --no-cache-dir -r requirements.txt

# Switch to non-root user
USER appuser

# Expose port 8000, then it will be exposed as 80
EXPOSE 8000

# Run the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]