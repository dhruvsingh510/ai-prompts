from typing import Dict, Any, Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field, ValidationError
from langchain_core.messages import SystemMessage, HumanMessage
import json
import re


class ApplicationAgent:
    def __init__(self, dynamic_variables: Dict[Any, Any], logger):
        self.logger = logger
        self.llm = dynamic_variables.get("llm")

    def create_collect_kyc_details_tool(self):

        class KYCOutput(BaseModel):
            phone_number: Optional[str]
            aadhaar_number: Optional[str]

        class KYCRequest(BaseModel):
            raw_user_input: str
            existing_phone_number: Optional[str] = None
            existing_aadhaar_number: Optional[str] = None

        @tool(
            "collect_kyc_details",
            description="Extracts and validates phone and Aadhaar details. Merges with existing state safely.",
            args_schema=KYCRequest,
        )
        def collect_kyc_details(
            raw_user_input: str,
            existing_phone_number: Optional[str] = None,
            existing_aadhaar_number: Optional[str] = None,
        ) -> Dict[str, Any]:

            try:
                system_prompt = """
You are a structured data extraction engine.

Extract:
- phone_number (10 digit Indian number)
- aadhaar_number (12 digit number)

Rules:
- Remove spaces and dashes.
- Do not invent data.
- If not found in THIS message, return null.
- Output strictly valid JSON.
"""

                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=raw_user_input)
                ]

                response = self.llm.invoke(messages)
                extracted_json = json.loads(response.content)
                validated_data = KYCOutput(**extracted_json)

                # --------------------------
                # Merge With Existing State
                # --------------------------
                phone_raw = validated_data.phone_number or existing_phone_number
                aadhaar_raw = validated_data.aadhaar_number or existing_aadhaar_number

                phone_clean = None
                aadhaar_clean = None
                phone_valid = False
                aadhaar_valid = False
                invalid_fields = []

                # --------------------------
                # Validate Phone
                # --------------------------
                if phone_raw:
                    phone_clean = re.sub(r"\D", "", phone_raw)
                    if len(phone_clean) == 10 and phone_clean[0] in ["6", "7", "8", "9"]:
                        phone_valid = True
                    else:
                        invalid_fields.append("phone_number")
                else:
                    invalid_fields.append("phone_number")

                # --------------------------
                # Validate Aadhaar
                # --------------------------
                if aadhaar_raw:
                    aadhaar_clean = re.sub(r"\D", "", aadhaar_raw)
                    if len(aadhaar_clean) == 12:
                        aadhaar_valid = True
                    else:
                        invalid_fields.append("aadhaar_number")
                else:
                    invalid_fields.append("aadhaar_number")

                # --------------------------
                # Determine Final State
                # --------------------------
                if phone_valid and aadhaar_valid:
                    application_status = "kyc_collected"
                elif phone_raw or aadhaar_raw:
                    application_status = "kyc_invalid"
                else:
                    application_status = "kyc_pending"

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

            except ValidationError as ve:
                self.logger.error(f"KYC validation error: {ve}")
                return {
                    "error": "Structured validation failed.",
                    "status": "failed"
                }

            except Exception as e:
                self.logger.error(f"KYC parsing error: {e}")
                return {
                    "error": str(e),
                    "status": "failed"
                }

        return collect_kyc_details

    def get_tools(self):
        return [self.create_collect_kyc_details_tool()]