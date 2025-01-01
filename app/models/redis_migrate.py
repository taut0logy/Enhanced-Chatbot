from redis_om import Migrator

if __name__ == "__main__":
    Migrator().run()
    print("Migrations completed.")