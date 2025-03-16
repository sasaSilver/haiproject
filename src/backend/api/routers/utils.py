from typing import Annotated

from pydantic.types import StringConstraints

Lowercase = Annotated[str, StringConstraints(pattern=r"^[A-Za-z]+$", to_lower=True)]
