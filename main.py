from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
import pandas as pd
from connection.engine_factory import EngineFactory

app = FastAPI()
templates = Jinja2Templates(directory="templates")

query = """
    select * from petmate.pm_animal_dtl
"""

engine = EngineFactory.create_engine_DEV_by('petmate')


def get_items(skip: int = 0, limit: int = 20):
    # SQL 쿼리에 limit과 offset 추가
    modified_query = query + f" LIMIT {limit} OFFSET {skip}"
    df = pd.read_sql(modified_query, con=engine)
    return df.to_dict(orient='records')


@app.get("/")
async def root(skip: int = 0, limit: int = 20):
    items = get_items(skip=skip, limit=limit)
    return templates.TemplateResponse("items.html", {"request": {}, "items": items, "skip": skip})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
