from db.queries import init_db


class DatabaseInitializer():
    def __init__(self):
        self.start_db()

    def start_db(self):
        init_db()
        
    