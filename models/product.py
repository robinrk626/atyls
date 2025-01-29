from pydantic import BaseModel

class ProductModel(BaseModel):
  productTitle: str
  productPrice: float
  imagePath: str
  
  def to_dict(self):
    return {"Title": self.productTitle, "price": self.productPrice, 'imagePath': self.imagePath }
