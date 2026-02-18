"""
データモデル定義
各サービスで使用するPydanticモデルを定義
"""

from models.scout_models import (
    AiResult,
    ResultsContainer,
    CreatePromptModel,
    ScoutMaterialModel
)

from models.jd_models import (
    OfferingContentModel,
    BussinessDescriptionModel
)

from models.screening_models import (
    ScreeningResult,
    ScreeningResultsContainer,
)

__all__ = [
    # Scout models
    "AiResult",
    "ResultsContainer",
    "CreatePromptModel",
    "ScoutMaterialModel",
    # JD models
    "OfferingContentModel",
    "BussinessDescriptionModel",
    # Screening models
    "ScreeningResult",
    "ScreeningResultsContainer",
]
