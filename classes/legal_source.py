class LegalSource:
    def __init__(self, id=None, title=None, source_link=None):
        self.id = id
        self.title = title
        self.source_link = source_link
    #suppose that data already inserted manually in database for source in sprint 2
    def get_source(self,conn):
        cursor = conn.cursor()
        cursor.execute("SELECT link FROM legal_source")
        source = cursor.fetchall()[0][0]
        cursor.close()
        return source
