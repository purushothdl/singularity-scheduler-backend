# Install project dependencies (creates venv if needed)
install:
	@if not exist venv python -m venv venv
	venv\Scripts\pip install -r requirements.txt

# Start the FastAPI server (activates venv automatically)
run:
	venv\Scripts\python -m uvicorn app.main:app --reload --port $(PORT)

# Start the FastAPI server with 0.0.0.0 binding
run-public:
	venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port $(PORT)
