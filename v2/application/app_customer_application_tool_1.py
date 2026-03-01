from typing import Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class ApplicationStartTool:
    def __init__(self, dynamic_variables: Dict[Any, Any], logger):
        self.logger = logger

    def create_start_application_tool(self):

        class StartApplicationRequest(BaseModel):
            user_confirmation: str = Field(
                description="User response confirming whether they want to start the application (yes/no)"
            )

        @tool(
            "start_application",
            description="Starts the credit card application. Call this when the user confirms they want to proceed with the recommended card. After application starts, KYC details must be collected.",
            args_schema=StartApplicationRequest,
        )
        def start_application(
            user_confirmation: str,
        ) -> Dict[str, Any]:
            try:
                confirmation = user_confirmation.strip().lower()

                if confirmation not in ["yes", "y"]:
                    return {
                        "message": "Application has not been started.",
                        "application_status": "not_started",
                        "status": "success"
                    }

                self.logger.info("Application started successfully")
                return {
                    "message": (
                        "Your application has been started successfully. "
                        "We now need to collect your KYC details to proceed."
                    ),
                    "application_status": "application_started_kyc_pending",
                    "next_step": "collect_kyc_details",
                    "status": "success"
                }

            except Exception as e:
                self.logger.error(f"Start application error: {e}")
                return {
                    "error": str(e),
                    "status": "failed"
                }

        return start_application

    def get_tools(self):
        return [self.create_start_application_tool()]