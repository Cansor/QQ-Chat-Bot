from pydantic import BaseModel


class Config(BaseModel):
    at_sender: bool = False


__all__ = [
    'Config'
]
