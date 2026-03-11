from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.models.registration import SiteRegistration
from app.schemas.registration import RegistrationCreate, RegistrationCreateResponse


router = APIRouter()
settings = get_settings()


@router.post("", response_model=RegistrationCreateResponse, status_code=201)
@limiter.limit(settings.rate_limit_create_registration)
def create_registration(
    payload: RegistrationCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> RegistrationCreateResponse:
    registration = SiteRegistration(
        full_name=payload.fullName.strip(),
        status=payload.status.value,
        email=str(payload.email).lower(),
        adult18=payload.adult18.value if payload.adult18 else None,
        region=payload.region.strip() if payload.region else None,
        participant_status=payload.participantStatus.value if payload.participantStatus else None,
        track=payload.track.value if payload.track else None,
        transport=payload.transport.value,
        car_number=payload.carNumber,
        passport=payload.passport.replace(" ", ""),
    )

    try:
        db.add(registration)
        db.commit()
        db.refresh(registration)
    except IntegrityError:
        db.rollback()
        return JSONResponse(
            status_code=409,
            content={
                "status": "duplicate",
                "errors": ["Registration with this email already exists"],
            },
        )
    except SQLAlchemyError as exc:
        db.rollback()
        raise RuntimeError("database_error") from exc

    return RegistrationCreateResponse(id=registration.id, createdAt=registration.created_at)
