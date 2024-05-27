from pydantic import BaseModel


class Image(BaseModel):
    base64Image: str
    imageTypeId: int
