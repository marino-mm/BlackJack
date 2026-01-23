uvicorn backend.server:app --port 8080

cd frontend
npm run dev

# Unitest 
python -m unittest backend.tests.model_test