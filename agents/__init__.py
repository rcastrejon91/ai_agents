from agents.finance_agent import FinanceAgent
from agents.legal_agent import LegalAgent
from agents.healthcare_agent import HealthcareAgent
from agents.retail_agent import RetailAgent
from agents.concierge_agent import ConciergeAgent

REGISTRY = {
    "finance": FinanceAgent,
    "legal": LegalAgent,
    "healthcare": HealthcareAgent,
    "retail": RetailAgent,
    "concierge": ConciergeAgent,
}
