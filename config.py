import sqlalchemy as sa, logging, sys, pandas as pd, pymysql
from sqlalchemy.exc import SQLAlchemyError


class logger:
    def __init__(self):
        self.logger = logging.getLogger('table_generator')
        self.logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler(filename='./table_generator.log',mode='a')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s:%(name)s: %(message)s',datefmt="%H:%M:%S"))

        console = logging.StreamHandler()
        console.setLevel(logging.ERROR)
        console.setFormatter(logging.Formatter('%(asctime)s %(levelname)s:%(name)s: %(message)s'))

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console)

class database(logger):
    def __init__(self, query: str, connection_string: str, limit: list):
        self.conn_string = connection_string
        self.query = query
        self.limit = limit

        self.dialect = self.extract_dialect()
        self.engine = self.connect_to_database()
        super().__init__()

    def extract_dialect(self) -> str:
        dialect = self.conn_string.split('://')
        self.conn_string = dialect[1]

        if dialect[0] == "mysql":
            return "mysql+pymysql"
        elif dialect[1] == "postgresql":
            return "postgresql+psycopg2"
        else:
            return ""

    def connect_to_database(self):
        try:
            engine = sa.create_engine(f'{self.dialect}://{self.conn_string}')
        except SQLAlchemyError as err:
            self.logger.error(f'Could not connect to database: {err}')
            return f'Could not connect to database: {err}'
        return engine
    
    def query_database(self):
        self.query = self.query + f' limit {self.limit[0]},{self.limit[len(self.limit)-1]}'
        try:
            df = pd.read_sql_query(sql=self.query, con=self.engine)
        except BaseException as e:
            self.logger.error(f'could not execute query: {e}')
            return f'could not execute query: {e}'
        return df