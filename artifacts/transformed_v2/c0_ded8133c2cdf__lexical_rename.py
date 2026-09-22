import datetime
import uuid
from dataclasses import dataclass

from app.core import BaseInteractorOutput, DbAddUserIn, IBTCWalletRepository


@dataclass
class UserInput:
    name: str


@dataclass
class UserOutput(BaseInteractorOutput):
    name: str
    api_key_renamed: str
    create_date_utc: datetime.datetime


@dataclass
class UserInteractor:
    @staticmethod
    def add_user(
        btc_wallet_repository: IBTCWalletRepository, user: UserInput
    ) -> UserOutput:

        api_key_renamed = uuid.uuid4().hex
        create_date_utc = datetime.datetime.now()
        us = btc_wallet_repository.add_user(
            DbAddUserIn(
                name=user.name, api_key_renamed=api_key_renamed, create_date_utc=create_date_utc
            )
        )

        return UserOutput(
            name=us.name,
            api_key_renamed=us.api_key_renamed,
            create_date_utc=us.create_date_utc,
            result_code=us.result_code,
        )