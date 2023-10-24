from sqlalchemy.engine.create import create_engine
from config.environ import Environ


class EngineFactory:

    @staticmethod
    def get_db_url(user, password, host, port, dbname):
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"

    @classmethod
    def create_engine_DEV_by(cls, dbname, echo=True):
        db_url = cls.get_db_url(
            Environ.P_DB_USER
            , Environ.P_DB_PASS
            , Environ.P_DB_HOST
            , Environ.P_DB_PORT
            , dbname
        )
        engine = create_engine(db_url)
        return engine


if __name__ == '__main__':
    a = EngineFactory.create_engine_DEV_by('sbook')
    print(a)
