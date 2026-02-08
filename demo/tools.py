"""
Tool implementations for AutoGen-based
multi-agent procurement workflow.

All tools are:
- Deterministic
- Side-effect free
- Easy to replace with real services
"""

from typing import Dict, List
import random


# ---------------------------------------------------------------------
# Intake Agent Tools
# ---------------------------------------------------------------------

def extract_procurement_fields(text: str) -> Dict:
    """
    Extract structured procurement fields from free text.
    NOTE: This is a mocked deterministic extractor.
    """

    text_lower = text.lower()

    fields = {
        "item_name": "MacBook" if "macbook" in text_lower else None,
        "quantity": 50 if "50" in text_lower else None,
        "estimated_budget": 7500000 if "75" in text_lower or "75l" in text_lower else None,
        "currency": "INR",
        "department": "Engineering" if "hire" in text_lower else None,
        "timeline": "Next Quarter" if "quarter" in text_lower else None,
        "vendor_preference": "Apple Authorized Vendor" if "apple" in text_lower else None,
    }

    return fields


def validate_required_fields(fields: Dict) -> List[str]:
    """
    Identify missing required fields.
    """

    required = ["item_name", "quantity", "estimated_budget", "currency"]
    missing = [f for f in required if not fields.get(f)]

    return missing


# ---------------------------------------------------------------------
# Policy Agent Tools
# ---------------------------------------------------------------------

def check_policy(estimated_budget: int, category: str = "IT_EQUIPMENT") -> Dict:
    """
    Validate procurement against policy rules.
    """

    if estimated_budget >= 5000000:
        return {
            "policy_status": "SOFT_BLOCK",
            "message": "Approval required for purchases above 50L"
        }

    return {
        "policy_status": "NO_ISSUE",
        "message": "Within standard procurement limits"
    }


def approval_matrix(amount: int) -> str:
    """
    Determine approval authority.
    """

    if amount < 1000000:
        return "Manager Approval"
    elif amount < 5000000:
        return "Director Approval"
    else:
        return "VP Approval"


# ---------------------------------------------------------------------
# Finance Agent Tools
# ---------------------------------------------------------------------

def check_budget(department: str, amount: int) -> Dict:
    """
    Check departmental budget availability.
    """

    mock_budget = {
        "Engineering": 8000000,
        "Marketing": 3000000,
        "HR": 2000000
    }

    available = mock_budget.get(department, 0)

    return {
        "available_budget": available,
        "sufficient": available >= amount
    }


def forecast_spend(amount: int) -> str:
    """
    Identify spend risk pattern.
    """

    if amount > 7000000:
        return "HIGH"
    elif amount > 3000000:
        return "MEDIUM"
    return "LOW"


# ---------------------------------------------------------------------
# Vendor Risk Agent Tools
# ---------------------------------------------------------------------

def lookup_vendor(vendor_name: str) -> Dict:
    """
    Lookup vendor status in vendor registry.
    """

    approved_vendors = {
        "Apple Authorized Vendor": True,
        "Dell Preferred Partner": True
    }

    if vendor_name in approved_vendors:
        return {
            "vendor_name": vendor_name,
            "status": "APPROVED"
        }

    return {
        "vendor_name": vendor_name,
        "status": "UNKNOWN"
    }


def vendor_risk_score(vendor_name: str) -> Dict:
    """
    Return vendor risk rating.
    """

    risk_map = {
        "Apple Authorized Vendor": "LOW",
        "Dell Preferred Partner": "LOW"
    }

    return {
        "vendor_name": vendor_name,
        "risk_rating": risk_map.get(vendor_name, "MEDIUM"),
        "contract_in_place": vendor_name in risk_map
    }


# ---------------------------------------------------------------------
# Utility / Shared Tools (Optional)
# ---------------------------------------------------------------------

def generate_request_id() -> str:
    """
    Generate a mock procurement request ID.
    """

    return f"PR-{random.randint(10000, 99999)}"
