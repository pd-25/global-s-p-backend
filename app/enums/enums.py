from enum import Enum
class CategoryOrderBy(str, Enum):
    id = "id"
    created_at = "created_at"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"
