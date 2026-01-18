from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import yaml

from engine_spec import execute_yaml

app = FastAPI()


@app.post("/run")
async def run_workflow(request: Request):

    try:
        body = await request.body()
        text = body.decode()

        result = execute_yaml(text)

        return JSONResponse(result)

    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )
