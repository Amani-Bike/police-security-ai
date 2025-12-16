from backend.database.db_setup import Base, engine

print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)
print("All tables dropped.")
