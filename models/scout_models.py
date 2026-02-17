"""
Scoutサービスで使用するデータモデル
"""

from pydantic import BaseModel
from typing import List


class AiResult(BaseModel):
    """
    AIの結果を格納するモデル
    """
    id: str
    required_condition: bool
    welcome_condition: bool
    evaluation_reason: str
    evaluation_result: str
    scout_message: str


class ResultsContainer(BaseModel):
    """結果全体を格納するコンテナ"""
    results: List[AiResult]


class CreatePromptModel(BaseModel):
    """プロンプト作成用モデル"""
    common_skill_of_A: str
    difference_of_ab_and_c: str
    difference_of_a_and_b: str
    required_condition: str
    welcome_condition: str


class ScoutMaterialModel(BaseModel):
    """スカウト素材モデル"""
    persona: str
    category: str
    industry: str
    keyword: str
    income: str
    desired_income: str
    scout_title: str
    scout_body: str
