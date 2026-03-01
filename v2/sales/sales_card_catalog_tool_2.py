from typing import Dict, Any, List
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class CreditCardCatalog:
    def __init__(self, dynamic_variables: Dict[Any, Any], logger):
        self.logger = logger

        # --- Centralized Card Database ---
        self.credit_cards = [
            {
                "card_name": "Platinum Travel Card",
                "min_age": 21,
                "min_monthly_income": 100000,
                "eligible_employment_status": ["employed", "self-employed"],
                "annual_fee": 5000,
                "primary_benefit": "travel",
                "reward_type": "travel_points",
                "reward_rate": "5X on flights, 2X on hotels",
                "lounge_access": True,
                "welcome_bonus": "10,000 travel points"
            },
            {
                "card_name": "Cashback Gold Card",
                "min_age": 18,
                "min_monthly_income": 40000,
                "eligible_employment_status": ["employed", "self-employed", "retired"],
                "annual_fee": 999,
                "primary_benefit": "shopping",
                "reward_type": "cashback",
                "reward_rate": "5% on online shopping, 1% elsewhere",
                "lounge_access": False,
                "welcome_bonus": "₹2000 cashback"
            },
            {
                "card_name": "Rewards Plus Card",
                "min_age": 18,
                "min_monthly_income": 30000,
                "eligible_employment_status": ["employed", "self-employed", "retired"],
                "annual_fee": 499,
                "primary_benefit": "dining",
                "reward_type": "reward_points",
                "reward_rate": "3X on dining, 1X on other spends",
                "lounge_access": False,
                "welcome_bonus": "5,000 reward points"
            },
            {
                "card_name": "Fuel Saver Card",
                "min_age": 18,
                "min_monthly_income": 25000,
                "eligible_employment_status": ["employed", "self-employed"],
                "annual_fee": 0,
                "primary_benefit": "fuel",
                "reward_type": "cashback",
                "reward_rate": "5% cashback on fuel",
                "lounge_access": False,
                "welcome_bonus": "Fuel surcharge waiver"
            },
            {
                "card_name": "Black Infinite Card",
                "min_age": 25,
                "min_monthly_income": 200000,
                "eligible_employment_status": ["employed", "self-employed"],
                "annual_fee": 10000,
                "primary_benefit": "premium",
                "reward_type": "points",
                "reward_rate": "10X on all spends",
                "lounge_access": True,
                "welcome_bonus": "₹50,000 points + complimentary lounge passes"
            },
            {
                "card_name": "Business Elite Card",
                "min_age": 21,
                "min_monthly_income": 75000,
                "eligible_employment_status": ["self-employed", "business_owner"],
                "annual_fee": 2999,
                "primary_benefit": "business",
                "reward_type": "cashback",
                "reward_rate": "3% on business spends, 1.5% on other",
                "lounge_access": True,
                "welcome_bonus": "₹15,000 cashback"
            },
            {
                "card_name": "Student Starter Card",
                "min_age": 18,
                "min_monthly_income": 10000,
                "eligible_employment_status": ["student", "employed"],
                "annual_fee": 0,
                "primary_benefit": "student",
                "reward_type": "cashback",
                "reward_rate": "2% on education, 1% on shopping",
                "lounge_access": False,
                "welcome_bonus": "₹500 cashback"
            },
            {
                "card_name": "Entertainment Plus Card",
                "min_age": 18,
                "min_monthly_income": 35000,
                "eligible_employment_status": ["employed", "self-employed", "retired"],
                "annual_fee": 799,
                "primary_benefit": "entertainment",
                "reward_type": "points",
                "reward_rate": "4X on movies/concerts, 2X on dining",
                "lounge_access": False,
                "welcome_bonus": "2 free movie tickets"
            },
            {
                "card_name": "Grocery & Essentials Card",
                "min_age": 18,
                "min_monthly_income": 20000,
                "eligible_employment_status": ["employed", "self-employed", "retired", "homemaker"],
                "annual_fee": 299,
                "primary_benefit": "grocery",
                "reward_type": "cashback",
                "reward_rate": "3% on grocery, 1% on all spends",
                "lounge_access": False,
                "welcome_bonus": "₹1000 cashback"
            },
            {
                "card_name": "Premium Shopping Card",
                "min_age": 21,
                "min_monthly_income": 50000,
                "eligible_employment_status": ["employed", "self-employed"],
                "annual_fee": 1499,
                "primary_benefit": "shopping",
                "reward_type": "points",
                "reward_rate": "6X on shopping malls, 3X on online",
                "lounge_access": True,
                "welcome_bonus": "₹10,000 shopping voucher"
            },
            {
                "card_name": "Healthcare Priority Card",
                "min_age": 18,
                "min_monthly_income": 30000,
                "eligible_employment_status": ["employed", "self-employed", "retired"],
                "annual_fee": 599,
                "primary_benefit": "healthcare",
                "reward_type": "cashback",
                "reward_rate": "5% on hospital/pharmacy, 2% on wellness",
                "lounge_access": False,
                "welcome_bonus": "Free health check-up"
            }
        ]

    # ----------------------------------------------------
    # Tool 1: List All Cards (Summary View)
    # ----------------------------------------------------
    def create_list_credit_cards_tool(self):

        @tool(
            "list_credit_cards",
            description="Returns a summary list of all available credit cards.",
        )
        def list_credit_cards() -> Dict[str, Any]:
            try:
                summary = [
                    {
                        "card_name": card["card_name"],
                        "primary_benefit": card["primary_benefit"],
                        "annual_fee": card["annual_fee"],
                        "min_monthly_income": card["min_monthly_income"]
                    }
                    for card in self.credit_cards
                ]

                self.logger.info("Listed all credit cards")

                return {
                    "cards": summary,
                    "status": "success"
                }

            except Exception as e:
                self.logger.error(f"List cards error: {e}")
                return {"error": str(e), "status": "failed"}

        return list_credit_cards

    # ----------------------------------------------------
    # Tool 2: Get Full Details for Specific Card
    # ----------------------------------------------------
    def create_get_card_details_tool(self):

        class CardRequest(BaseModel):
            card_name: str = Field(
                description="Name of the credit card"
            )

        @tool(
            "get_card_details",
            description="Returns full details and eligibility criteria for a specific credit card.",
            args_schema=CardRequest,
        )
        def get_card_details(card_name: str) -> Dict[str, Any]:
            try:
                for card in self.credit_cards:
                    if card["card_name"].lower() == card_name.lower():
                        self.logger.info(f"Fetched details for {card_name}")
                        return {
                            "card_details": card,
                            "status": "success"
                        }

                return {
                    "error": "Card not found",
                    "status": "failed"
                }

            except Exception as e:
                self.logger.error(f"Get card details error: {e}")
                return {"error": str(e), "status": "failed"}

        return get_card_details

    def get_tools(self):
        return [
            self.create_list_credit_cards_tool(),
            self.create_get_card_details_tool()
        ]