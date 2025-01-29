from fastapi import Header, FastAPI, HTTPException, Depends, Request
from config.config import Settings
from redis import Redis
from models import ScraperSettings
from utils import getRedisCredentials
from modules import Scrapers, Products
from services import RedisClient
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

def authenticate(token: str):
  return token and token == Settings.token

@app.middleware("http")
async def authenticateMiddleware(request: Request, call_next):
  token = request.headers.get("Authorization")
  if token is None or not authenticate(token):
    raise HTTPException(status_code=401, detail="Invalid Token")
  response = await call_next(request)
  return response
  
@app.get('/health')
async def health():
  return { "healthy": "healthy" }

@app.post("/scrape/")
def start_scraping(
  settings: ScraperSettings,
  redisCredentials: Redis = Depends(getRedisCredentials)
):
  redis = RedisClient(redisCredentials)
  scraper = Scrapers(settings, redis, Products.saveProducts, Products.saveProductImage )
  scrape_response: dict = scraper.startScraping()
  scrape_response['statusCode'] = "200"
  scrape_response['message'] = "Scraping Completed"
  return scrape_response
