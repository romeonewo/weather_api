.PHONY: install run test docker-up docker-down clean lint

# Install dependencies
install:
	pip install -r requirements.txt

# Run the application
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	pytest -v

# Run tests with coverage
test-cov:
	pytest --cov=app --cov-report=html

# Start all services with Docker
docker-up:
	docker-compose up -d

# Stop all services
docker-down:
	docker-compose down

# Start Redis only
redis:
	docker-compose up -d redis

# Run application in production mode
prod:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Load test the alerts endpoint (requires Apache Bench)
load-test:
	ab -n 1000 -c 10 http://localhost:8000/alerts

# Clean up cache and temporary files
clean:
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov

# Lint code
lint:
	flake8 app/ tests/ --max-line-length=100
