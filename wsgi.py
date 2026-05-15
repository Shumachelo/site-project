import os
from main import app, api
from data import db_session

if os.environ.get('RENDER'):
    db_path = "/tmp/auction.db"
else:
    os.makedirs("db", exist_ok=True)
    db_path = "db/auction.db"

db_session.global_init(db_path)

if __name__ == "__main__":
    app.run()