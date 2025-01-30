from typing import List
from models import ProductModel
from config.config import Settings
import os
import requests
import json

class Products:
    
  def saveProducts(products: List[ProductModel]):
    try:
      filePath = Settings.fileToWriteRecords
      try:
        with open(filePath, 'r') as file:
          fileData = json.load(file)
      except (FileNotFoundError, json.JSONDecodeError):
        fileData = []
      fileData.extend([item.to_dict() for item in products])

      with open(filePath, 'w') as file:
        json.dump(fileData, file, indent=4)

      print(f"Successfully appended data to {filePath}")
    except Exception as e:
      print(f"Error: {e}")
  
  def saveProductImage(imageUrl: str, imageName: str) -> str:
    try:
      folder = Settings.imageFolder
      os.makedirs(folder,exist_ok = True)
      response = requests.get(imageUrl, stream = True)
      response.raise_for_status()
      imagePath = os.path.join(folder, imageName)
      with open(imagePath, 'wb') as file:
        file.write(response.content)
      return imagePath
    except:
      print('Failed to save image in folder')
      return ''