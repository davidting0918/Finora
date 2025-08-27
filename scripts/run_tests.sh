#!/bin/bash

export PYTEST_RUNNING=1

cd backend

echo "Running tests..."
python -m pytest tests/ -v --tb=short

echo "Tests completed!"
