from redis import Redis
from typing import Optional

class RedisClient:
  
  def __init__(self, redisClient: Redis):
    print(redisClient)
    self.client = redisClient

  def getKey(self, key: str) -> Optional[str]:
    return self.client.get(key)

  def setKey(self, key: str, value: str, expiry: int):
    self.client.setex(key, expiry, value)