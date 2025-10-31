web: python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
release: python -c "import asyncio; from app.core.database import init_db; asyncio.run(init_db())"