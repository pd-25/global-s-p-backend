
from slugify import slugify
import uuid
from datetime import datetime

def generate_slug(text: str) -> str:
    return slugify(text)


def generate_enquiry_number():
    date_str = datetime.now().strftime("%d%m%Y")
    short_id = str(uuid.uuid4().int)[:6]  # short unique number
    return f"GSE-{date_str}-{short_id}"
