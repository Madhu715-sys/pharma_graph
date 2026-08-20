import os
from neo4j import GraphDatabase, exceptions
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("COGNODB_URI")
USER = os.getenv("COGNODB_USER", "cognodb")
PASSWORD = os.getenv("COGNODB_PASSWORD")

class CognoDBManager:
    def __init__(self):
        self._driver = None

    def get_driver(self):
        if self._driver is None:
            if not URI or not PASSWORD:
                raise ValueError("COGNODB_URI and COGNODB_PASSWORD must be set in .env")
            try:
                self._driver = GraphDatabase.driver(
                    URI,
                    auth=(USER, PASSWORD),
                    max_connection_lifetime=30 * 60,
                    keep_alive=True,
                    connection_timeout=30.0
                )
                self._driver.verify_connectivity()
                print("-> Connected to CognoDB successfully.")
            except exceptions.ServiceUnavailable as e:
                print(f"[!] CognoDB connection error: {e}")
                self._driver = None
            except Exception as e:
                print(f"[!] Unexpected error: {e}")
                self._driver = None
        return self._driver

    def close(self):
        if self._driver is not None:
            try:
                self._driver.close()
            except Exception:
                pass
            self._driver = None
            print("-> CognoDB driver closed.")

db_manager = CognoDBManager()