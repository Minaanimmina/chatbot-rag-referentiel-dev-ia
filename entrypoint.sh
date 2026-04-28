#!/bin/bash

if [ ! -d "chromadb_vector_database" ] || [ -z "$(ls -A chromadb_vector_database)" ]; then
    echo "Base vectorielle absente, ingestion en cours..."
    python -m ingest
else
    echo "Base vectorielle déjà présente, ingestion ignorée."
fi

chainlit run app.py --host 0.0.0.0 --port 8000