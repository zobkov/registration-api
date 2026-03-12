from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, model_validator


class RegistrationStatus(str, Enum):
    speaker = "speaker"
    participant = "participant"
    guest = "guest"


class TransportType(str, Enum):
    private = "Личный транспорт"
    public = "Общественный транспорт"
    transfer = "Спец. развозка от КБК"
    online = "Онлайн"


class Adult18(str, Enum):
    yes = "Да"
    no = "Нет"


class ParticipantStatus(str, Enum):
    secondary = "Среднее образование"
    higher = "Высшее образование"
    employed = "Работаю"


class Track(str, Enum):
    finance = "finance"
    logistics = "logistics"
    consulting = "consulting"
    politics = "politics"
    marketing = "marketing"
    language = "language"
    chinese = "chinese"
    rosmolodezh_grants = "rosmolodezh_grants"


class RegistrationCreate(BaseModel):
    fullName: str = Field(min_length=2, max_length=200)
    status: RegistrationStatus
    transport: TransportType
    carNumber: str | None = Field(default=None, max_length=24)
    passport: str = Field(min_length=3, max_length=30)
    adult18: Adult18 | None = None
    region: str | None = Field(default=None, min_length=2, max_length=120)
    participantStatus: ParticipantStatus | None = None
    email: EmailStr
    track: Track | None = None

    @model_validator(mode="after")
    def validate_conditional_rules(self) -> "RegistrationCreate":
        if self.transport == TransportType.private and not self.carNumber:
            raise ValueError("carNumber is required when transport is 'Личный транспорт'")
        if self.transport == TransportType.online and self.carNumber is not None:
            raise ValueError("carNumber must be null when transport is 'Онлайн'")

        if self.status == RegistrationStatus.participant:
            if not self.adult18:
                raise ValueError("adult18 is required for participant")
            if not self.region:
                raise ValueError("region is required for participant")
            if not self.participantStatus:
                raise ValueError("participantStatus is required for participant")
            if not self.track:
                raise ValueError("track is required for participant")

        return self


class RegistrationCreateResponse(BaseModel):
    id: str
    numericKey: str
    status: str = "created"
    createdAt: datetime


class ApiError(BaseModel):
    status: str
    errors: list[str]
