"""
Screeningサービスで使用するデータモデル
"""

from pydantic import BaseModel
from typing import List


class ScreeningResult(BaseModel):
    """書類選考結果モデル"""
    evaluation_reason: str
    required_condition: bool
    welcome_condition: bool
    evaluation_result: str

class ScreeningResultsContainer(BaseModel):
    """結果全体を格納するコンテナ"""
    results: List[ScreeningResult]