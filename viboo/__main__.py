"""
Entry point for the execution.
"""
import uvicorn
import os

import viboo.server

if __name__ == "__main__":
    port = os.environ.get("PORT", 8080)
    host = os.environ.get("HOST", "0.0.0.0")
    viboo.server.setup_database()
    uvicorn.run("server:app", host=host, port=port, log_level="info")



