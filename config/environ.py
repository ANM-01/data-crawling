import os
from dotenv import load_dotenv

load_dotenv()


class Environ:

    P_DB_HOST = os.environ['P_DB_HOST']
    P_DB_PORT = os.environ['P_DB_PORT']
    P_DB_USER = os.environ['P_DB_USER']
    P_DB_PASS = os.environ['P_DB_PASS']
