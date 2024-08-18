import logging
import traceback
from fastapi import Request , status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError , HTTPException

async def validationExceptionHandler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    #error_messages = {error['loc'][0]: error['msg'] for error in errors}
    error_messages = "\n".join([error['msg'] for error in errors])
    logging.error(f"[validationExceptionHandler] Request Validation Error : {request.method} {request.url} error_message : {error_messages}")
    logging.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"msg": error_messages},
    )
    
async def httpExceptionHandler(request: Request, exc: HTTPException):
    error_message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    logging.error(f"[httpExceptionHandler] Request Validation Error : {request.method} {request.url} error_message : {error_message}")
    logging.error(traceback.format_exc())
    return JSONResponse(content={"msg": error_message}, status_code=exc.status_code)