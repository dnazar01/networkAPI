import enum


class SortType(enum.Enum):
    ASCENDING = "asc"
    DESCENDING = "desc"


class Status(enum.Enum):
    DELETED = "deleted"
    CREATED = "created"

class Person:
    def __init__(self):
        self.status = Status.DELETED.value

p = Person()
print(p.status)
