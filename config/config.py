import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
  siteUrl = 'https://dentalstall.com/shop'
  startChallengeUrl = 'https://dentalstall.com/hcdn-cgi/jschallenge'
  validateChallengeUrl = 'https://dentalstall.com/hcdn-cgi/jschallenge-validate'
  token = "atlysdentalstall"
  redisHost = os.getenv("REDIS_HOST")
  redisPort = os.getenv("REDIS_PORT")
  imageFolder = '../images'
  fileToWriteRecords = '../products.json'