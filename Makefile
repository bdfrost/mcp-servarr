.PHONY: build run test clean deploy k8s-deploy k8s-delete help

# Variables
IMAGE_NAME := mcp-servarr
IMAGE_TAG := latest
NAMESPACE := mcp-servarr

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build Docker image
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

run: ## Run with docker-compose
	docker-compose up

run-detached: ## Run with docker-compose in background
	docker-compose up -d

stop: ## Stop docker-compose
	docker-compose down

logs: ## View docker-compose logs
	docker-compose logs -f

test: ## Run tests
	python -m pytest tests/ -v

clean: ## Clean up containers and images
	docker-compose down -v
	docker rmi $(IMAGE_NAME):$(IMAGE_TAG) || true

k8s-deploy: ## Deploy to Kubernetes
	kubectl apply -f k8s/deployment.yaml

k8s-delete: ## Delete from Kubernetes
	kubectl delete -f k8s/deployment.yaml

k8s-logs: ## View Kubernetes logs
	kubectl logs -n $(NAMESPACE) -l app=mcp-servarr -f

k8s-status: ## Check Kubernetes deployment status
	kubectl get all -n $(NAMESPACE)

k8s-describe: ## Describe Kubernetes deployment
	kubectl describe deployment mcp-servarr -n $(NAMESPACE)

lint: ## Run Python linter
	python -m flake8 src/ --max-line-length=120

format: ## Format Python code
	python -m black src/

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install pytest flake8 black

dev: ## Run in development mode
	python src/server.py
