from redis import Redis
from config.config import Settings

def getRedisCredentials():
  return Redis(host=Settings.redisHost, port=Settings.redisPort)
  