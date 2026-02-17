"""
JD(Job Description)サービスで使用するデータモデル
"""

from pydantic import BaseModel


class OfferingContentModel(BaseModel):
    """募集職種内容モデル"""
    background: str
    job_category: str
    required_requirement: str
    welcome_requirement: str
    character_statue: str


class BussinessDescriptionModel(BaseModel):
    """事業説明モデル"""
    company_name: str
    business_service_name: str
    company_philosophy: str
    business_introduction: str
    business_detail: str
