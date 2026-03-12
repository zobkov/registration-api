from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.numeric_key import generate_numeric_key
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.models.registration import SiteRegistration
from app.schemas.registration import RegistrationCreate, RegistrationCreateResponse


router = APIRouter()
settings = get_settings()
MAX_NUMERIC_KEY_RETRIES = 5


def _extract_constraint_name(exc: IntegrityError) -> str | None:
    diag = getattr(getattr(exc, "orig", None), "diag", None)
    return getattr(diag, "constraint_name", None)


def _is_numeric_key_conflict(exc: IntegrityError) -> bool:
    constraint_name = _extract_constraint_name(exc)
    if constraint_name == "uq_site_registrations_numeric_key":
        return True

    message = str(getattr(exc, "orig", exc)).lower()
    return "numeric_key" in message and "unique" in message


def _is_email_conflict(exc: IntegrityError) -> bool:
    constraint_name = _extract_constraint_name(exc)
    if constraint_name == "uq_site_registrations_email":
        return True

    message = str(getattr(exc, "orig", exc)).lower()
    return "email" in message and "unique" in message


@router.post("", response_model=RegistrationCreateResponse, status_code=201)
@limiter.limit(settings.rate_limit_create_registration)
def create_registration(
    payload: RegistrationCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> RegistrationCreateResponse:
    for attempt in range(MAX_NUMERIC_KEY_RETRIES):
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
            passport=payload.passport.replace(" ", "") if payload.passport else None,
            education=payload.education,
            numeric_key=generate_numeric_key(),
        )

        try:
            db.add(registration)
            db.commit()
            db.refresh(registration)
            return RegistrationCreateResponse(
                id=registration.id,
                numericKey=registration.numeric_key,
                createdAt=registration.created_at,
            )
        except IntegrityError as exc:
            db.rollback()

            if _is_numeric_key_conflict(exc) and attempt < MAX_NUMERIC_KEY_RETRIES - 1:
                continue

            if _is_email_conflict(exc):
                return JSONResponse(
                    status_code=409,
                    content={
                        "status": "duplicate",
                        "errors": ["Registration with this email already exists"],
                    },
                )

            raise RuntimeError("database_integrity_error") from exc
        except SQLAlchemyError as exc:
            db.rollback()
            raise RuntimeError("database_error") from exc

    raise RuntimeError("numeric_key_generation_exhausted")
