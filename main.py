from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
import pandas as pd
from connection.engine_factory import EngineFactory

myapi = FastAPI()
templates = Jinja2Templates(directory="templates")

query = """
    select * from petmate.pm_destiny_info;
"""
vaccin_query = {
    "dog": "select * from petmate.pm_vaccin_info where animal_id = 1;",
    "cat": "select * from petmate.pm_vaccin_info where animal_id = 2;"  # 고양이 정보 예시
}


engine = EngineFactory.create_engine_DEV_by('petmate')


def get_items(skip: int = 0, limit: int = 20):
    # SQL 쿼리에 limit과 offset 추가
    modified_query = query + f" LIMIT {limit} OFFSET {skip}"
    df = pd.read_sql(modified_query, con=engine)
    return df.to_dict(orient='records')

def get_vaccin(animal_type, skip=0, limit=20):
    # SQL 쿼리에 limit과 offset 추가
    modified_query = vaccin_query[animal_type] + f" LIMIT {limit} OFFSET {skip}"
    df = pd.read_sql(modified_query, con=engine)
    return df.to_dict(orient='records')


@myapi.get("/")
async def root(skip: int = 0, limit: int = 20):
    items = get_items(skip=skip, limit=limit)
    return templates.TemplateResponse("items.html", {"request": {}, "items": items, "skip": skip})

@myapi.get("/vaccin_{animal_type}")
async def vaccin(animal_type: str, skip: int = 0, limit: int = 20):
    items = get_vaccin(animal_type, skip, limit)
    return templates.TemplateResponse("vaccin.html", {"request": {}, "items": items, "skip": skip})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(myapi, host="0.0.0.0", port=8000)
