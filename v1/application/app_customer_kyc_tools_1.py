from typing import Dict, Any, Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import re


class KycAgent:
    def __init__(self, dynamic_variables: Dict[Any, Any], logger):
        self.logger = logger

    def create_collect_kyc_details_tool(self):

        class KYCRequest(BaseModel):
            phone_number: Optional[str] = Field(
                default=None,
                description="10-digit Indian mobile number"
            )
            aadhaar_number: Optional[str] = Field(
                default=None,
                description="12-digit Aadhaar number"
            )

        @tool(
            "collect_kyc_details",
            description="Validates phone number and Aadhaar number for KYC. Pass each field individually after collecting from the user.",
            args_schema=KYCRequest,
        )
        def collect_kyc_details(
            phone_number: Optional[str] = None,
            aadhaar_number: Optional[str] = None,
        ) -> Dict[str, Any]:

            try:
                phone_clean = None
                aadhaar_clean = None
                phone_valid = False
                aadhaar_valid = False
                invalid_fields = []

                # --------------------------
                # Validate Phone
                # --------------------------
                if phone_number:
                    phone_clean = re.sub(r"\D", "", phone_number)
                    if len(phone_clean) == 10 and phone_clean[0] in ["6", "7", "8", "9"]:
                        phone_valid = True
                    else:
                        invalid_fields.append("phone_number")
                else:
                    invalid_fields.append("phone_number")

                # --------------------------
                # Validate Aadhaar
                # --------------------------
                if aadhaar_number:
                    aadhaar_clean = re.sub(r"\D", "", aadhaar_number)
                    if len(aadhaar_clean) == 12:
                        aadhaar_valid = True
                    else:
                        invalid_fields.append("aadhaar_number")
                else:
                    invalid_fields.append("aadhaar_number")

                # --------------------------
                # Determine Status
                # --------------------------
                if phone_valid and aadhaar_valid:
                    application_status = "kyc_collected"
                else:
                    application_status = "kyc_invalid"

                self.logger.info(f"KYC validation result: phone={phone_valid}, aadhaar={aadhaar_valid}")

                return {
                    "phone_number": phone_clean,
                    "aadhaar_number": aadhaar_clean,
                    "phone_valid": phone_valid,
                    "aadhaar_valid": aadhaar_valid,
                    "invalid_fields": invalid_fields,
                    "kyc_valid": phone_valid and aadhaar_valid,
                    "application_status": application_status,
                    "status": "success"
                }

            except Exception as e:
                self.logger.error(f"KYC parsing error: {e}")
                return {
                    "error": str(e),
                    "status": "failed"
                }

        return collect_kyc_details

    def create_submit_application_tool(self):

        class SubmitApplicationRequest(BaseModel):
            phone_number: str = Field(description="Validated 10-digit phone number")
            aadhaar_number: str = Field(description="Validated 12-digit Aadhaar number")
            user_confirmation: str = Field(description="User confirmation to submit (yes/no)")

        @tool(
            "submit_application",
            description="Submits the credit card application after KYC is validated and user confirms. Only call after collect_kyc_details returns kyc_valid=true and user confirms submission.",
            args_schema=SubmitApplicationRequest,
        )
        def submit_application(
            phone_number: str,
            aadhaar_number: str,
            user_confirmation: str,
        ) -> Dict[str, Any]:
            try:
                confirmation = user_confirmation.strip().lower()

                if confirmation not in ["yes", "y"]:
                    return {
                        "message": "Application submission cancelled by user.",
                        "application_status": "kyc_collected",
                        "status": "success"
                    }

                self.logger.info("Application submitted successfully")
                return {
                    "message": (
                        "Your credit card application has been submitted successfully! "
                        "You will receive a confirmation shortly."
                    ),
                    "application_status": "submitted",
                    "status": "success"
                }

            except Exception as e:
                self.logger.error(f"Submit application error: {e}")
                return {
                    "error": str(e),
                    "status": "failed"
                }

        return submit_application

    def get_tools(self):
        return [
            self.create_collect_kyc_details_tool(),
            self.create_submit_application_tool(),
        ]