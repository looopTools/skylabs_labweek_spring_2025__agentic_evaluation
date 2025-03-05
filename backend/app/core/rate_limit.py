from datetime import datetime, timedelta
from typing import Dict, Tuple
from fastapi import HTTPException, Request
from app.core.config import settings

# Store request counts with timestamps
request_store: Dict[str, Tuple[int, datetime]] = {}

async def rate_limit_middleware(request: Request):
    """Rate limiting middleware"""
    # Get client IP
    client_ip = request.client.host
    now = datetime.now()
    
    # Check and update request count
    if client_ip in request_store:
        count, start_time = request_store[client_ip]
        # Reset counter if outside the 1-minute window
        if now - start_time > timedelta(minutes=1):
            request_store[client_ip] = (1, now)
        else:
            # Increment counter if within window
            count += 1
            if count > settings.RATE_LIMIT_PER_MINUTE:
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later."
                )
            request_store[client_ip] = (count, start_time)
    else:
        # First request from this IP
        request_store[client_ip] = (1, now)