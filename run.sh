#!/bin/bash
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please edit .env and add your OPENAI_API_KEY"
    exit 1
fi

source venv/bin/activate
python main.py
