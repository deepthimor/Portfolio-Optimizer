from backend.database import Base, engine
from backend import models


def main():
    Base.metadata.create_all(bind=engine)
    print("tables created")


if __name__ == "__main__":
    main()