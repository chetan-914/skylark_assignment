#!/bin/bash
# Start FastAPI (Backend)
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Start Streamlit (Frontend)
streamlit run ui/streamlit_app.py --server.port 7860 --server.address 0.0.0.0