from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class SmolexConfig:
    roots: List[str]
    exclude: List[str]
    extensions: List[str]
    ast_sqlite_db: str
    vector_store_location: str

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


# TODO: Move this to a config file
config = SmolexConfig.from_dict(
    {
        "roots": ["/Users/livioso/Code/lolex/src", "/Users/livioso/Code/lolex/test"],
        "extensions": [".py"],
        "exclude": ["ui/res/*.py"],
        "ast_sqlite_db": "/tmp/smolex_ast_info.db",
        "vector_store_location": "/tmp/smolex_vector_store",
    }
)
