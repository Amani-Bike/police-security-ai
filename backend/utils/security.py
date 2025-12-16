import bcrypt

MAX_BCRYPT_LEN = 72  # bcrypt max

def hash_password(password: str) -> str:
    truncated = password[:MAX_BCRYPT_LEN].encode('utf-8')
    hashed = bcrypt.hashpw(truncated, bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    truncated = plain_password[:MAX_BCRYPT_LEN].encode('utf-8')
    return bcrypt.checkpw(truncated, hashed_password.encode('utf-8'))
