from slowapi import Limiter
from slowapi.util import get_remote_address

# Single global limiter instance
limiter = Limiter(key_func=get_remote_address)