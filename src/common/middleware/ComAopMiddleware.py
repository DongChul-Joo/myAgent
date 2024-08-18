# AOP 미들웨어
import logging
import traceback
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.exceptions import HTTPException
from starlette.requests import Request
from fastapi.responses import Response , JSONResponse

class AopMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            # 요청 전에 수행할 로깅
            logging.info(f"[ComAopMiddleware] Request Start: {request.method} {request.url}")

            # 요청 본문 읽기
            request_body = await request.body()
            #logging.info(f"[ComAopMiddleware] Request Body: %s" , request_body)

            # 요청 객체를 다시 생성
            request = Request(request.scope, receive=lambda: request_body)

            # 다음 미들웨어 또는 핸들러 호출
            response = await call_next(request)
            
            # 응답 본문 읽기
            response_body = [section async for section in response.body_iterator]
            response_body_bytes = b''.join(response_body)
            response_body_str = response_body_bytes.decode()

            # 응답 본문 다시 설정 및 Content-Length 헤더 업데이트
            response = Response(
                content=response_body_bytes,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            response.headers['Content-Length'] = str(len(response_body_bytes))

            # 응답 후에 수행할 로깅
            logging.info(f"[ComAopMiddleware] Request End: {request.method} {request.url} {response_body_str}")
        
            return response
        except Exception as e:
            logging.error(f"[ComAopMiddleware] Not Define Exception!! : {request.method} {request.url} error_message : {str(e)}")
            logging.error(traceback.format_exc())
            return JSONResponse(content={"msg" : "알 수 없는 에러가 발생했습니다."} , status_code=500)