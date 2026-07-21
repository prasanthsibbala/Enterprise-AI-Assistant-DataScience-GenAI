from datetime import datetime
from io import BytesIO

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)
from fastapi.responses import (
    StreamingResponse,
)

from app.dependencies.auth import CurrentUser
from app.schemas.report import FraudReportRequest
from app.services.report_service import (
    report_service,
)

router = APIRouter()


@router.post(
    "/reports/fraud/pdf",
    status_code=status.HTTP_200_OK,
)
def generate_fraud_report(
    request: FraudReportRequest,
    current_user: CurrentUser,
) -> StreamingResponse:
    try:
        pdf_bytes = (
            report_service.generate_fraud_report(
                request
            )
        )

        filename = (
            "healthcare_fraud_report_"
            f"{datetime.now():%Y%m%d_%H%M%S}.pdf"
        )

        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{filename}"'
                )
            },
        )

    except Exception as error:
        print(
            "PDF generation error: "
            f"{type(error).__name__}: {error}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Unable to generate PDF report."
            ),
        ) from error