from enum import Enum
class CategoryOrderBy(str, Enum):
    id = "id"
    created_at = "created_at"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

class EnquiryStatus(str, Enum):
    pending = "Pending"
    in_progress = "In Progress"
    replied = "Replied"
    closed = "Closed"
    on_hold = "On Hold"
    not_interested = "Not Interested"
    not_relevant = "Not Relevant"
    spam = "Spam"
    other = "Other"

class EnquiryType(str, Enum):
    inquiry = "inquiry"
    quote = "quote"

    
    
