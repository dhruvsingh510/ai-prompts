from typing import Dict, Any, Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class CustomerProfileParser:
    def __init__(self, dynamic_variables: Dict[Any, Any], logger):
        self.logger = logger

    def create_customer_profile_parser(self):

        class CustomerProfileRequest(BaseModel):
            date_of_birth: Optional[str] = Field(
                default=None,
                description="Date of birth in DD-MM-YYYY format"
            )
            monthly_income: Optional[float] = Field(
                default=None,
                description="Monthly income as numeric value"
            )
            employment_status: Optional[str] = Field(
                default=None,
                description="Employment status (employed, self-employed, retired, student, unemployed)"
            )
            primary_spend_category: Optional[str] = Field(
                default=None,
                description="Primary spending category (travel, shopping, dining, fuel, grocery, entertainment, healthcare, business, premium)"
            )
            reward_preference: Optional[str] = Field(
                default=None,
                description="Reward preference (cashback, reward_points, travel_points, points)"
            )
            lounge_access_preference: Optional[bool] = Field(
                default=None,
                description="Whether the user wants lounge access (True/False)"
            )

        @tool(
            "customer_profile_parser",
            description="Parses and validates structured customer profile data required for credit card recommendation. Pass each field individually.",
            args_schema=CustomerProfileRequest,
        )
        def customer_profile_parser(
            date_of_birth: Optional[str] = None,
            monthly_income: Optional[float] = None,
            employment_status: Optional[str] = None,
            primary_spend_category: Optional[str] = None,
            reward_preference: Optional[str] = None,
            lounge_access_preference: Optional[bool] = None,
        ) -> Dict[str, Any]:
            try:
                # Normalize employment status
                if employment_status:
                    employment_status = employment_status.strip().lower()

                # Normalize spend category
                if primary_spend_category:
                    primary_spend_category = primary_spend_category.strip().lower()

                # Normalize reward preference
                if reward_preference:
                    reward_preference = reward_preference.strip().lower()

                self.logger.info("Customer profile parsed successfully")
                return {
                    "date_of_birth": date_of_birth,
                    "monthly_income": monthly_income,
                    "employment_status": employment_status,
                    "primary_spend_category": primary_spend_category,
                    "reward_preference": reward_preference,
                    "lounge_access_preference": lounge_access_preference,
                    "status": "success"
                }

            except Exception as e:
                self.logger.error(f"Parsing error: {e}")
                return {
                    "error": str(e),
                    "status": "failed"
                }

        return customer_profile_parser

    def get_tools(self):
        return [self.create_customer_profile_parser()]