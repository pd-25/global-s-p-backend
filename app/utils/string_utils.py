
import re
from slugify import slugify

def generate_slug(text: str) -> str:
    return slugify(text)
