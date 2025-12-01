.PHONY: build build-local run run-local run-detached run-local-detached stop stop-local logs logs-local test clean deploy k8s-deploy k8s-delete help

# Variables
IMAGE_NAME := mcp-servarr
IMAGE_TAG := latest
LOCAL_TAG := local
NAMESPACE := mcp-servarr

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build Docker image (REST API mode)
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

build-local: ## Build Docker image (MCP stdio mode)
	docker build -f Dockerfile.local -t $(IMAGE_NAME):$(LOCAL_TAG) .

build-all: ## Build both Docker images
	$(MAKE) build
	$(MAKE) build-local

run: ## Run REST API mode with docker-compose
	docker-compose up

run-local: ## Run MCP stdio mode with docker-compose
	docker-compose -f docker-compose.local.yml up

run-detached: ## Run REST API mode in background
	docker-compose up -d

run-local-detached: ## Run MCP stdio mode in background
	docker-compose -f docker-compose.local.yml up -d

stop: ## Stop REST API mode docker-compose
	docker-compose down

stop-local: ## Stop MCP stdio mode docker-compose
	docker-compose -f docker-compose.local.yml down

logs: ## View REST API mode docker-compose logs
	docker-compose logs -f

logs-local: ## View MCP stdio mode docker-compose logs
	docker-compose -f docker-compose.local.yml logs -f

test: ## Run tests
	python -m pytest tests/ -v

clean: ## Clean up all containers and images
	docker-compose down -v
	docker-compose -f docker-compose.local.yml down -v
	docker rmi $(IMAGE_NAME):$(IMAGE_TAG) || true
	docker rmi $(IMAGE_NAME):$(LOCAL_TAG) || true

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
