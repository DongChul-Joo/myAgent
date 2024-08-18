from fastapi import Request
from starlette.datastructures import Headers

def getRemoteIp(request: Request) -> str:
    headers = Headers(request.headers)
    
    remote_ip = headers.get("X-Forwarded-For")
    
    if not remote_ip or remote_ip.lower() == "unknown":
        remote_ip = headers.get("Proxy-Client-IP")
    
    if not remote_ip or remote_ip.lower() == "unknown":
        remote_ip = headers.get("WL-Proxy-Client-IP")
    
    if not remote_ip or remote_ip.lower() == "unknown":
        remote_ip = headers.get("HTTP_CLIENT_IP")
    
    if not remote_ip or remote_ip.lower() == "unknown":
        remote_ip = headers.get("HTTP_X_FORWARDED_FOR")
    
    if not remote_ip or remote_ip.lower() == "unknown":
        remote_ip = request.client.host
    
    return remote_ip