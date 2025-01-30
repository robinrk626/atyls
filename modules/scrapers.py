from bs4 import BeautifulSoup
from models import ScraperSettings
from services import RedisClient
from typing import Callable, List
from models import ProductModel
from config.config import Settings
import requests
import hashlib
import re
import time

class Scrapers:

  def __init__(self, settings: ScraperSettings, redis: RedisClient, saveProducts: Callable[[List[ProductModel]], None], saveImage: Callable[[str, str], str]):
    self.settings = settings
    self.redis = redis
    self.saveProducts = saveProducts
    self.requestSession = requests.session()
    self.saveImage = saveImage
    if settings.proxy:
      self.requestSession.proxies = {
        "http": settings.proxy,
        "https": settings.proxy,
      }
  
  def getChallengeId(self, siteUrl: str) -> str:
    try:
      headers = dict({
        'referer': siteUrl,
        "user-agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
      })
      response = self.requestSession.get(Settings.startChallengeUrl, headers = headers, timeout= 100 )
      if response.status_code == 200:
        responseData = response.text
        cjsToken = responseData.split(';')[0].split("'")[1]
        return hashlib.sha256(cjsToken.encode()).hexdigest()
    except:
      return ''
  
  def getCookies(self, siteUrl: str) -> str:
    try:
      challengeId = self.getChallengeId(siteUrl)
      body = {
        "challenge": challengeId
      }
      headers = {
        "user-agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
      }
      response = self.requestSession.post(Settings.validateChallengeUrl, headers = headers, data = body)
      if response.status_code==200:
        return response.headers['Set-Cookie']
    except:
      return ''
  
  def getPageHtml(self, siteUrl: str) -> str:
    try:
      cookie = self.getCookies(siteUrl)
      headers = {
        "Cookie": cookie,
        "user-agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
      }
      maxRetries = 5
      while maxRetries:
        response = self.requestSession.get(siteUrl, headers = headers)
        if response.status_code == 200:
          return response.text
        maxRetries -= 1
        time.sleep(2)
      return ''
    except:
      return ''
  
  def fetchProductItemsFromHtml(self, htmlContent: str, productItems: List, scrapResponse: dict):
    try:
      soup = BeautifulSoup(htmlContent, 'html.parser')
      productItemsHtml = soup.find_all('li', class_='product')
      scrapResponse['totalProducts'] += len(productItemsHtml)
      for productItem in productItemsHtml:
        title = str(productItem.find('div', class_='mf-product-thumbnail').find('a').find('img')['alt'])
        title = title.replace('- Dentalstall India','').strip()
        price = productItem.find('span', class_='price').find('bdi').get_text(strip=True)
        price = re.findall(r'[\d.]+', price)
        price = str('-0.0' if len(price) == 0 else price[0])
        imageUrl = productItem.find('div', class_='mf-product-thumbnail').find('a').find('img')['data-lazy-src']
        redisKey = "product_" + title.replace(' ', '_')
        cachedPrice = self.redis.getKey(redisKey)
        if cachedPrice is not None:
          cachedPrice = cachedPrice.decode("utf-8")
        if cachedPrice == price:
          continue
        if cachedPrice == None:
          scrapResponse['newProducts'] += 1
        else:
          scrapResponse['updatedProducts'] += 1
        imagePath = self.saveImage(imageUrl = imageUrl, imageName = title)
        self.redis.setKey(redisKey, price, 3600)
        productItems.append(ProductModel(productTitle = title,productPrice = float(price),imagePath = imagePath))
    except:
      return
  
  def startScraping(self) -> dict:
    response = dict({
      'newProducts': 0,
      'totalProducts': 0,
      'updatedProducts': 0,
    })
    productItems = []
    for pageNo in range(1, self.settings.maxPages+1):
      siteUrl = Settings.siteUrl + "/page/" + str(pageNo)
      htmlContent = self.getPageHtml(siteUrl)
      self.fetchProductItemsFromHtml(htmlContent, productItems, response)
    self.saveProducts(products = productItems)
    return response