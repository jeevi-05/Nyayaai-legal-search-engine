from typing import Generic, Optional, TypeVar, List
from pydantic import BaseModel


T = TypeVar("T")


# ==========================================================
# Common API Response Schema
# Used by auth, users, dashboard, documents APIs
# ==========================================================

class ApiResponse(BaseModel, Generic[T]):

    success: bool
    message: str
    data: Optional[T] = None


    @classmethod
    def ok(cls, message: str, data=None):
        return cls(
            success=True,
            message=message,
            data=data
        )


    @classmethod
    def error(cls, message: str, data=None):
        return cls(
            success=False,
            message=message,
            data=data
        )



# ==========================================================
# Module 4 - Role Based Dashboard Response
# ==========================================================

class DashboardResponse(BaseModel):

    role: str

    dashboard_name: str

    features: List[str]



# ==========================================================
# Dashboard Statistics
# ==========================================================

class DashboardStats(BaseModel):

    total_documents: int

    total_cases: int

    total_acts: int

    total_judgements: int



# ==========================================================
# Civilian Dashboard
# ==========================================================

class CivilianDashboard(BaseModel):

    role: str = "CIVILIAN"

    dashboard_name: str = "Civilian Legal Assistance Portal"

    features: List[str] = [
        "Search Legal Information",
        "View Acts and Rights",
        "Understand Legal Terms"
    ]



# ==========================================================
# Lawyer Dashboard
# ==========================================================

class LawyerDashboard(BaseModel):

    role: str = "LAWYER"

    dashboard_name: str = "Lawyer Research Portal"

    features: List[str] = [
        "Legal Case Search",
        "Precedent Research",
        "Decision Support",
        "Save Important Cases"
    ]



# ==========================================================
# Judge Dashboard
# ==========================================================

class JudgeDashboard(BaseModel):

    role: str = "JUDGE"

    dashboard_name: str = "Judicial Intelligence Portal"

    features: List[str] = [
        "View Case Information",
        "Review Similar Judgments",
        "Access Legal Principles"
    ]



# ==========================================================
# Police / Investigator Dashboard
# ==========================================================

class PoliceDashboard(BaseModel):

    role: str = "POLICE"

    dashboard_name: str = "Investigation Support Portal"

    features: List[str] = [
        "Search Relevant Laws",
        "Find Previous Cases",
        "View Legal Sections"
    ]



# ==========================================================
# Admin Dashboard
# ==========================================================

class AdminDashboard(BaseModel):

    role: str = "ADMIN"

    dashboard_name: str = "Administration Portal"

    features: List[str] = [
        "Upload Documents",
        "Manage Legal Repository",
        "View Statistics",
        "Manage Users"
    ]