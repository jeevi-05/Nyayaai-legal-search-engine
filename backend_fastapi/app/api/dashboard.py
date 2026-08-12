from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.schemas.dashboard import DashboardResponse
from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User, Role


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


dashboard_data = {


    Role.CIVILIAN: {

        "dashboard_name":
        "Civilian Legal Assistance Portal",

        "features":[
            "Search Legal Information",
            "View Acts and Rights",
            "Understand Legal Terms"
        ]
    },


    Role.LAWYER: {

        "dashboard_name":
        "Lawyer Research Portal",

        "features":[
            "Legal Case Search",
            "Precedent Research",
            "Decision Support",
            "Save Important Cases"
        ]
    },


    Role.JUDGE: {

        "dashboard_name":
        "Judicial Intelligence Portal",

        "features":[
            "View Case Information",
            "Review Similar Judgments",
            "Access Legal Principles"
        ]
    },


    Role.POLICE: {

        "dashboard_name":
        "Investigation Support Portal",

        "features":[
            "Search Relevant Laws",
            "Find Previous Cases",
            "View Legal Sections"
        ]
    },


    Role.ADMIN: {

        "dashboard_name":
        "Administration Portal",

        "features":[
            "Upload Documents",
            "Manage Legal Repository",
            "View Statistics",
            "Manage Users"
        ]
    }

}



@router.get(
    "/me",
    response_model=DashboardResponse
)
def get_dashboard(
    current_user: User = Depends(get_current_user)
):

    role = current_user.role


    dashboard = dashboard_data.get(
        role,
        dashboard_data[Role.CIVILIAN]
    )


    return {

        "role": role.value,

        "dashboard_name":
        dashboard["dashboard_name"],

        "features":
        dashboard["features"]

    }