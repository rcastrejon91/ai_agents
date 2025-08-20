from agents.concierge_agent import ConciergeAgent
from agents.finance_agent import FinanceAgent
from agents.healthcare_agent import HealthcareAgent
from agents.legal_agent import LegalAgent
from agents.retail_agent import RetailAgent

REGISTRY = {
    "finance": FinanceAgent,
    "legal": LegalAgent,
    "healthcare": HealthcareAgent,
    "retail": RetailAgent,
    "concierge": ConciergeAgent,
}
