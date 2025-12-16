from backend.database.db_setup import Base, engine
from backend.models.user_model import User

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database and tables created successfully!")

if __name__ == "__main__":
    init_db()
