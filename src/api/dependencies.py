from typing import Annotated

from fastapi import Depends

from .repositories import *

UserRepo = Annotated[UserRepository, Depends(UserRepository.get_repo)]
MovieRepo = Annotated[MovieRepository, Depends(MovieRepository.get_repo)]
RatingRepo = Annotated[RatingRepository, Depends(RatingRepository.get_repo)]
