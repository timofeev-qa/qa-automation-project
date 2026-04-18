from db.queries import init_db


class DBClient():
    def __init__(self):
        self.start_db()

    def start_db(self):
        init_db()
        
    