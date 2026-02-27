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
            application_status: str = Field(
                description="Current application status"
            )

        @tool(
            "start_application",
            description="Starts the credit card application depending on KYC completion status.",
            args_schema=StartApplicationRequest,
        )
        def start_application(
            user_confirmation: str,
            application_status: str,
        ) -> Dict[str, Any]:

            try:
                confirmation = user_confirmation.strip().lower()

                if confirmation not in ["yes", "y"]:
                    return {
                        "message": "Application has not been started.",
                        "application_status": application_status,
                        "status": "success"
                    }

                # User confirmed yes
                if application_status == "kyc_pending":
                    return {
                        "message": (
                            "Your KYC verification is still under progress. "
                            "The application will start once KYC is completed."
                        ),
                        "application_status": "kyc_pending",
                        "status": "success"
                    }

                elif application_status == "kyc_invalid":
                    return {
                        "message": (
                            "Your KYC details are invalid. "
                            "Please re-submit your phone number and Aadhaar to proceed."
                        ),
                        "application_status": "kyc_invalid",
                        "status": "success"
                    }

                elif application_status == "kyc_collected":
                    self.logger.info("Application started successfully")

                    return {
                        "message": (
                            "Your application has been successfully started. "
                            "KYC verification is complete."
                        ),
                        "application_status": "under_review",
                        "status": "success"
                    }

                else:
                    return {
                        "message": "Application cannot be started in the current state.",
                        "application_status": application_status,
                        "status": "failed"
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