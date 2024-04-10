import enum


class SortType(enum.Enum):
    ASCENDING = "asc"
    DESCENDING = "desc"


class Status(enum.Enum):
    DELETED = "deleted"
    CREATED = "created"
