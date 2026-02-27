from typing import Dict, Any, List
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from datetime import datetime


class CustomerEligibilityChecker:
    def __init__(self, dynamic_variables: Dict[Any, Any], logger):
        self.logger = logger

    def create_customer_eligibility_checker(self):

        # Define input schema
        class EligibilityRequest(BaseModel):
            date_of_birth: str = Field(
                description="Customer date of birth in DD-MM-YYYY format"
            )
            employment_status: str = Field(
                description="Customer employment status"
            )
            monthly_income: float = Field(
                description="Customer monthly income"
            )

            # Card-specific eligibility criteria
            card_name: str = Field(
                description="Name of the credit card"
            )
            min_age: int = Field(
                description="Minimum age required for the card"
            )
            min_monthly_income: float = Field(
                description="Minimum monthly income required for the card"
            )
            eligible_employment_status: List[str] = Field(
                description="List of allowed employment statuses for the card"
            )

        @tool(
            "customer_eligibility_checker",
            description="Checks customer eligibility for a specific credit card based on age, income, and employment rules.",
            args_schema=EligibilityRequest,
        )
        def customer_eligibility_checker(
            date_of_birth: str,
            employment_status: str,
            monthly_income: float,
            card_name: str,
            min_age: int,
            min_monthly_income: float,
            eligible_employment_status: List[str],
        ) -> Dict[str, Any]:

            try:
                # --- Calculate Age ---
                dob = datetime.strptime(date_of_birth, "%d-%m-%Y")
                today = datetime.today()
                age = today.year - dob.year - (
                    (today.month, today.day) < (dob.month, dob.day)
                )

                normalized_status = employment_status.strip().lower()
                normalized_allowed_status = [
                    status.lower() for status in eligible_employment_status
                ]

                # --- Eligibility Checks ---
                age_valid = age >= min_age
                income_valid = monthly_income >= min_monthly_income
                employment_valid = normalized_status in normalized_allowed_status

                is_eligible = age_valid and income_valid and employment_valid

                self.logger.info(
                    f"Eligibility check executed for card: {card_name}"
                )

                return {
                    "card_name": card_name,
                    "age": age,
                    "monthly_income": monthly_income,
                    "employment_status": normalized_status,
                    "age_valid": age_valid,
                    "income_valid": income_valid,
                    "employment_valid": employment_valid,
                    "eligible": is_eligible,
                    "status": "success"
                }

            except ValueError:
                self.logger.error("Invalid date format provided")
                return {
                    "error": "Invalid date format. Expected YYYY-MM-DD.",
                    "status": "failed"
                }

            except Exception as e:
                self.logger.error(f"Eligibility tool error: {e}")
                return {
                    "error": str(e),
                    "status": "failed"
                }

        return customer_eligibility_checker

    def get_tools(self):
        return [self.create_customer_eligibility_checker()]