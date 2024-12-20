from typing import List
from dotenv import load_dotenv

from fastapi import Depends, FastAPI, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.models.exception.http_json_exception import HttpJsonException
from src.models.response.health_response_dto import HealthResponseDto

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


""" HttpJsonException
"""


@app.exception_handler(HttpJsonException)
async def unicorn_exception_handler(request: Request, exc: HttpJsonException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "statusCode": exc.status_code,
            "errorMessage": exc.error_message,
        },
    )


### Health API
### This is Health API List

""" [GET] /
    Args:
        None
    Returns:
        HealthResponseDto
"""


@app.get("/", status_code=status.HTTP_200_OK, response_model=HealthResponseDto)
async def health():
    try:
        return HealthResponseDto(status="OK")
    except Exception as e:
        print("Exception occurred:", e)
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )
