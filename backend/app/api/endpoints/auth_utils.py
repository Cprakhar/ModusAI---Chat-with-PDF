from fastapi import Header, HTTPException

def get_token_from_header(authorization: str = Header(...)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    return authorization.split(" ", 1)[1]
