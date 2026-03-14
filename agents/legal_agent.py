# agents/legal_agent.py

"""
Legal Agent - Legal research, contract analysis, compliance, and advisory
"""

from agents.base import SyncAgent
from typing import Dict, List, Optional
import re


class LegalAgent(SyncAgent):
    """
    Specialized agent for legal research, contract analysis, and compliance
    """
    
    name = "legal"
    description = "Legal research, contract analysis, compliance checking, and advisory"
    capabilities = [
        "legal_research",
        "contract_analysis",
        "compliance_checking",
        "risk_assessment",
        "document_review",
        "regulatory_guidance",
        "intellectual_property",
        "employment_law",
        "business_law"
    ]
    
    def define_personality(self) -> Dict:
        return {
            "type": "LegalAgent",
            "traits": [
                "precise",
                "thorough",
                "analytical",
                "cautious",
                "detail-oriented",
                "objective"
            ],
            "communication_style": "formal yet accessible",
            "expertise": [
                "contract law",
                "corporate law",
                "intellectual property",
                "employment law",
                "regulatory compliance",
                "risk management"
            ]
        }
    
    def load_tools(self) -> List:
        """Load legal-specific tools"""
        return [
            "case_law_database",
            "statute_search",
            "contract_analyzer",
            "compliance_checker",
            "risk_assessor",
            "legal_citation_formatter"
        ]
    
    def handle(self, message: str) -> str:
        """Handle legal requests"""
        
        message_lower = message.lower()
        
        # Route to appropriate handler
        if any(word in message_lower for word in ["contract", "agreement", "terms"]):
            return self._analyze_contract(message)
        
        elif any(word in message_lower for word in ["compliance", "regulation", "regulatory"]):
            return self._check_compliance(message)
        
        elif any(word in message_lower for word in ["trademark", "patent", "copyright", "ip"]):
            return self._handle_intellectual_property(message)
        
        elif any(word in message_lower for word in ["employment", "employee", "hire", "termination"]):
            return self._handle_employment_law(message)
        
        elif any(word in message_lower for word in ["liability", "risk", "exposure"]):
            return self._assess_risk(message)
        
        elif any(word in message_lower for word in ["privacy", "gdpr", "ccpa", "data protection"]):
            return self._handle_privacy_law(message)
        
        elif any(word in message_lower for word in ["startup", "incorporation", "llc", "business formation"]):
            return self._handle_business_formation(message)
        
        else:
            return self._general_legal_research(message)
    
    def _analyze_contract(self, message: str) -> str:
        """Analyze contracts and agreements"""
        return f"""
⚖️ **Contract Analysis**

**Request:** {message}

**Key Contract Elements to Review:**

**1. Essential Terms**
   ✓ Parties involved (proper legal names and addresses)
   ✓ Effective date and term/duration
   ✓ Consideration (what each party provides)
   ✓ Scope of work/deliverables
   ✓ Payment terms and schedule

**2. Critical Clauses to Examine**
   • **Termination Clause**
     - Notice period required
     - Grounds for termination
     - Post-termination obligations
   
   • **Liability & Indemnification**
     - Limitation of liability caps
     - Indemnification scope
     - Insurance requirements
   
   • **Intellectual Property**
     - Ownership of work product
     - License grants
     - Confidentiality obligations
   
   • **Dispute Resolution**
     - Governing law
     - Jurisdiction/venue
     - Arbitration vs. litigation
     - Attorney's fees provision

**3. Red Flags to Watch For**
   ⚠️ Automatic renewal clauses
   ⚠️ Unilateral modification rights
   ⚠️ Overly broad indemnification
   ⚠️ Unlimited liability exposure
   ⚠️ Non-compete restrictions
   ⚠️ Assignment restrictions

**4. Recommended Actions**
   1. Review all exhibits and schedules
   2. Verify signature authority
   3. Check for conflicting provisions
   4. Ensure mutual obligations are balanced
   5. Negotiate favorable terms where possible

**5. Standard Contract Checklist**
   □ All blanks filled in
   □ No handwritten modifications without initials
   □ All pages numbered and accounted for
   □ Proper execution (signatures, dates, titles)
   □ Counterparts clause if signing separately

**Next Steps:**
• Share specific contract for detailed review
• Identify your primary concerns
• Clarify your negotiation priorities

---
*This is general information, not legal advice. Consult a licensed attorney for your specific situation.*
        """.strip()
    
    def _check_compliance(self, message: str) -> str:
        """Check regulatory compliance"""
        return f"""
📋 **Compliance Analysis**

**Request:** {message}

**Key Regulatory Frameworks:**

**1. Data Privacy & Security**
   • **GDPR** (EU) - General Data Protection Regulation
     - Applies to: EU residents' data
     - Key requirements: Consent, data minimization, right to erasure
     - Penalties: Up to 4% of global revenue
   
   • **CCPA/CPRA** (California)
     - Applies to: California residents
     - Key requirements: Disclosure, opt-out rights, data deletion
     - Penalties: $2,500-$7,500 per violation
   
   • **HIPAA** (Healthcare)
     - Applies to: Protected health information
     - Key requirements: Privacy rule, security rule, breach notification
     - Penalties: $100-$50,000 per violation

**2. Financial Regulations**
   • **SOX** (Sarbanes-Oxley)
     - Applies to: Public companies
     - Key requirements: Internal controls, financial reporting
   
   • **PCI DSS** (Payment Card Industry)
     - Applies to: Organizations handling credit cards
     - Key requirements: Secure network, cardholder data protection
   
   • **AML/KYC** (Anti-Money Laundering)
     - Applies to: Financial institutions
     - Key requirements: Customer identification, suspicious activity reporting

**3. Employment & Labor**
   • **FLSA** (Fair Labor Standards Act)
     - Minimum wage, overtime, child labor
   
   • **FMLA** (Family Medical Leave Act)
     - Job-protected leave for qualifying events
   
   • **ADA** (Americans with Disabilities Act)
     - Reasonable accommodations, anti-discrimination

**4. Industry-Specific**
   • **FDA** - Food, drugs, medical devices
   • **FTC** - Consumer protection, advertising
   • **EPA** - Environmental regulations
   • **OSHA** - Workplace safety

**Compliance Checklist:**
   □ Identify applicable regulations
   □ Document compliance procedures
   □ Train employees on requirements
   □ Implement monitoring systems
   □ Conduct regular audits
   □ Maintain required records
   □ Establish incident response plan
   □ Review and update policies annually

**Risk Assessment:**
   • High Risk: Non-compliance penalties, reputational damage
   • Medium Risk: Operational disruptions, remediation costs
   • Low Risk: Administrative burdens, documentation requirements

**Recommended Actions:**
   1. Conduct compliance gap analysis
   2. Develop compliance program
   3. Assign compliance officer
   4. Implement training program
   5. Schedule regular audits

---
*This is general information, not legal advice. Consult a licensed attorney and compliance expert.*
        """.strip()
    
    def _handle_intellectual_property(self, message: str) -> str:
        """Handle IP matters"""
        return f"""
💡 **Intellectual Property Analysis**

**Request:** {message}

**Types of IP Protection:**

**1. Trademarks (™/®)**
   • **Protects:** Brand names, logos, slogans
   • **Duration:** 10 years, renewable indefinitely
   • **Requirements:** Use in commerce, distinctiveness
   • **Cost:** $250-$350 per class (USPTO filing)
   
   **Trademark Classes:**
   - Strong: Fanciful (Kodak), Arbitrary (Apple)
   - Moderate: Suggestive (Netflix)
   - Weak: Descriptive (may need secondary meaning)
   - Unprotectable: Generic (Computer Store)

**2. Patents**
   • **Utility Patent** - Inventions, processes
     - Duration: 20 years from filing
     - Cost: $5,000-$15,000+ (with attorney)
     - Requirements: Novel, non-obvious, useful
   
   • **Design Patent** - Ornamental designs
     - Duration: 15 years from grant
     - Cost: $2,000-$4,000
   
   • **Provisional Patent** - Temporary protection
     - Duration: 12 months
     - Cost: $70-$280 (filing fee)

**3. Copyrights (©)**
   • **Protects:** Original works of authorship
     - Literary works, software code
     - Music, art, photographs
     - Architectural works
   
   • **Duration:** Life + 70 years (individual)
                   95 years (corporate work-for-hire)
   
   • **Cost:** $45-$65 (registration)
   
   • **Rights:** Reproduction, distribution, derivative works

**4. Trade Secrets**
   • **Protects:** Confidential business information
   • **Duration:** Indefinite (if kept secret)
   • **Requirements:** 
     - Economic value from secrecy
     - Reasonable efforts to maintain secrecy
   • **Examples:** Coca-Cola formula, Google algorithm

**IP Strategy Recommendations:**

**For Startups:**
   1. Conduct trademark clearance search
   2. File trademark applications early
   3. Use NDAs with contractors/employees
   4. Include IP assignment clauses in contracts
   5. Document invention dates and processes
   6. Consider provisional patent for inventions

**For Established Businesses:**
   1. Audit existing IP portfolio
   2. Register core trademarks internationally
   3. Implement trade secret protection program
   4. Monitor for infringement
   5. License IP strategically
   6. Maintain IP insurance

**Common IP Pitfalls:**
   ⚠️ Public disclosure before patent filing
   ⚠️ Not securing IP assignments from contractors
   ⚠️ Using similar marks to competitors
   ⚠️ Failing to enforce IP rights
   ⚠️ Inadequate trade secret protection

**Next Steps:**
   • Identify your IP assets
   • Prioritize protection strategy
   • Budget for filing and maintenance
   • Consult IP attorney for filing

---
*This is general information, not legal advice. Consult a licensed IP attorney.*
        """.strip()
    
    def _handle_employment_law(self, message: str) -> str:
        """Handle employment law matters"""
        return f"""
👥 **Employment Law Guidance**

**Request:** {message}

**Key Employment Law Areas:**

**1. Hiring & Onboarding**
   • **Job Descriptions**
     - Clear duties and qualifications
     - Essential vs. non-essential functions
     - Avoid discriminatory language
   
   • **Interview Process**
     - Lawful questions only
     - Consistent process for all candidates
     - Document decision rationale
   
   • **Background Checks**
     - Obtain written consent (FCRA)
     - Provide adverse action notice if applicable
     - State-specific restrictions (e.g., ban-the-box)
   
   • **Offer Letters**
     - At-will employment statement
     - Compensation and benefits
     - Start date and contingencies

**2. Classification & Compensation**
   • **Employee vs. Independent Contractor**
     - IRS 20-factor test
     - ABC test (some states)
     - Misclassification penalties
   
   • **Exempt vs. Non-Exempt**
     - FLSA salary threshold: $684/week ($35,568/year)
     - Duties test (executive, administrative, professional)
     - Overtime requirements (1.5x for 40+ hours)
   
   • **Minimum Wage**
     - Federal: $7.25/hour
     - State/local may be higher
     - Tipped employees: Special rules

**3. Required Policies & Handbooks**
   □ Anti-discrimination and harassment
   □ Equal employment opportunity
   □ Leave policies (FMLA, sick, vacation)
   □ Meal and rest breaks (state-specific)
   □ Timekeeping and overtime
   □ Code of conduct
   □ Confidentiality and IP assignment
   □ Social media policy
   □ Drug and alcohol policy
   □ Workplace safety
   □ Complaint/grievance procedures

**4. Termination Best Practices**
   • **Documentation**
     - Performance issues and warnings
     - Policy violations
     - Improvement plans
   
   • **Termination Meeting**
     - Brief and professional
     - Two people present
     - Prepared severance/release (if applicable)
     - Return of company property
   
   • **Final Pay**
     - State-specific deadlines
     - Unused vacation (if required)
     - COBRA notice
   
   • **Unemployment Claims**
     - Respond timely
     - Provide documentation
     - Attend hearings if contested

**5. Protected Classes & Discrimination**
   Federal protections (EEOC):
   • Race, color, national origin
   • Sex (including pregnancy, gender identity)
   • Religion
   • Age (40+)
   • Disability
   • Genetic information
   
   State/local may add:
   • Sexual orientation
   • Marital status
   • Military status
   • Criminal history (some jurisdictions)

**6. Workplace Accommodations**
   • **ADA (Disabilities)**
     - Interactive process required
     - Reasonable accommodations
     - Undue hardship defense
   
   • **Religious Accommodations**
     - Dress code exceptions
     - Schedule modifications
     - De minimis cost standard

**7. Leave Laws**
   • **FMLA** - 12 weeks unpaid, job-protected
     - Applies to: 50+ employee companies
     - Qualifying events: Birth, adoption, serious health condition
   
   • **State Leave Laws** - May be more generous
     - Paid family leave (CA, NY, NJ, etc.)
     - Paid sick leave (many states/cities)

**Common Employment Law Mistakes:**
   ⚠️ Misclassifying employees as contractors
   ⚠️ Not paying overtime to non-exempt employees
   ⚠️ Retaliating against whistleblowers
   ⚠️ Inadequate harassment training
   ⚠️ Inconsistent policy enforcement
   ⚠️ Failing to provide required meal breaks

**Recommended Actions:**
   1. Audit current employment practices
   2. Update employee handbook
   3. Train managers on employment law
   4. Implement consistent documentation
   5. Review independent contractor relationships
   6. Conduct annual policy review

---
*This is general information, not legal advice. Consult an employment attorney.*
        """.strip()
    
    def _assess_risk(self, message: str) -> str:
        """Assess legal risks"""
        return f"""
⚠️ **Legal Risk Assessment**

**Request:** {message}

**Risk Assessment Framework:**

**1. Risk Categories**

   **High Risk (Immediate Action Required)**
   • Regulatory non-compliance with penalties
   • Uninsured liability exposure
   • Contract breaches with material damages
   • Employment law violations
   • IP infringement claims
   • Data breach/privacy violations

   **Medium Risk (Mitigation Recommended)**
   • Ambiguous contract terms
   • Inadequate insurance coverage
   • Weak IP protection
   • Incomplete corporate records
   • Vendor/supplier dependencies
   • Unclear employment policies

   **Low Risk (Monitor)**
   • Minor policy gaps
   • Administrative non-compliance
   • Documentation improvements needed
   • Process optimization opportunities

**2. Risk Mitigation Strategies**

   **Contractual Protection**
   • Limitation of liability clauses
   • Indemnification provisions
   • Insurance requirements
   • Dispute resolution mechanisms
   • Force majeure clauses
   • Termination rights

   **Insurance Coverage**
   • General liability insurance
   • Professional liability (E&O)
   • Directors & officers (D&O)
   • Cyber liability insurance
   • Employment practices liability (EPLI)
   • Commercial property insurance

   **Corporate Governance**
   • Proper entity formation/maintenance
   • Board meeting minutes
   • Shareholder agreements
   • Operating agreements (LLC)
   • Bylaws compliance
   • Annual filings

   **Compliance Programs**
   • Written policies and procedures
   • Employee training
   • Regular audits
   • Incident response plans
   • Documentation systems
   • Third-party assessments

**3. Industry-Specific Risks**

   **Technology/SaaS**
   • Data privacy and security
   • Service level agreements
   • IP ownership disputes
   • Open source licensing
   • Export control compliance

   **Healthcare**
   • HIPAA compliance
   • Medical malpractice
   • Billing fraud
   • Credentialing issues
   • Patient consent

   **Financial Services**
   • Regulatory compliance (SEC, FINRA)
   • Fiduciary duties
   • Anti-money laundering
   • Consumer protection
   • Cybersecurity

   **E-commerce/Retail**
   • Consumer protection laws
   • Product liability
   • Payment card compliance (PCI DSS)
   • Advertising regulations
   • Sales tax nexus

**4. Risk Assessment Checklist**

   □ Identify all potential legal exposures
   □ Quantify potential damages/costs
   □ Evaluate likelihood of occurrence
   □ Review existing protections
   □ Determine risk tolerance
   □ Prioritize mitigation efforts
   □ Implement controls and safeguards
   □ Monitor and reassess regularly

**5. Crisis Management**

   **Preparation**
   • Crisis response team
   • Communication protocols
   • Legal counsel on retainer
   • Insurance broker relationships
   • Document preservation procedures

   **Response**
   • Immediate legal counsel consultation
   • Preserve all relevant documents
   • Control communications
   • Notify insurance carriers
   • Comply with reporting obligations

**Recommended Actions:**
   1. Conduct comprehensive legal audit
   2. Review and update insurance coverage
   3. Implement compliance program
   4. Establish legal budget and reserves
   5. Create crisis response plan
   6. Schedule quarterly risk reviews

**Red Flags Requiring Immediate Attention:**
   🚨 Pending or threatened litigation
   🚨 Regulatory investigation or inquiry
   🚨 Material contract breach
   🚨 Data breach or security incident
   🚨 Employment discrimination claim
   🚨 IP infringement allegation

---
*This is general information, not legal advice. Consult a licensed attorney for risk assessment.*
        """.strip()
    
    def _handle_privacy_law(self, message: str) -> str:
        """Handle privacy and data protection"""
        return f"""
🔒 **Privacy & Data Protection**

**Request:** {message}

**Key Privacy Regulations:**

**1. GDPR (General Data Protection Regulation)**
   • **Scope:** EU residents' personal data
   • **Territorial:** Applies globally if processing EU data
   
   **Core Principles:**
   • Lawfulness, fairness, transparency
   • Purpose limitation
   • Data minimization
   • Accuracy
   • Storage limitation
   • Integrity and confidentiality
   
   **Individual Rights:**
   • Right to access
   • Right to rectification
   • Right to erasure ("right to be forgotten")
   • Right to data portability
   • Right to object
   • Rights related to automated decision-making
   
   **Requirements:**
   • Legal basis for processing (consent, contract, etc.)
   • Privacy notices
   • Data protection impact assessments (DPIAs)
   • Data processing agreements (DPAs)
   • Breach notification (72 hours)
   • Data Protection Officer (if required)
   
   **Penalties:** Up to €20M or 4% of global revenue

**2. CCPA/CPRA (California Consumer Privacy Act)**
   • **Scope:** California residents
   • **Threshold:** $25M revenue OR 50,000+ consumers OR 50%+ revenue from selling data
   
   **Consumer Rights:**
   • Right to know what data is collected
   • Right to delete personal information
   • Right to opt-out of sale
   • Right to non-discrimination
   • Right to correct inaccurate data (CPRA)
   • Right to limit use of sensitive data (CPRA)
   
   **Requirements:**
   • Privacy policy with specific disclosures
   • "Do Not Sell My Personal Information" link
   • Verified consumer request process
   • Service provider agreements
   • Reasonable security measures
   
   **Penalties:** $2,500 per violation ($7,500 if intentional)

**3. HIPAA (Health Insurance Portability and Accountability Act)**
   • **Scope:** Protected Health Information (PHI)
   • **Covered Entities:** Healthcare providers, health plans, clearinghouses
   • **Business Associates:** Vendors handling PHI
   
   **Requirements:**
   • Privacy Rule (use and disclosure limits)
   • Security Rule (administrative, physical, technical safeguards)
   • Breach Notification Rule
   • Business Associate Agreements (BAAs)
   
   **Penalties:** $100-$50,000 per violation (up to $1.5M annually)

**4. Other Privacy Laws**
   • **COPPA** - Children's Online Privacy Protection Act
   • **FERPA** - Family Educational Rights and Privacy Act
   • **GLBA** - Gramm-Leach-Bliley Act (financial)
   • **State Laws** - Virginia (VCDPA), Colorado (CPA), Connecticut, Utah, etc.

**Privacy Program Essentials:**

**1. Data Inventory & Mapping**
   □ What data is collected
   □ Why it's collected (purpose)
   □ Where it's stored
   □ Who has access
   □ How long it's retained
   □ Where it's transferred
   □ Third parties with access

**2. Privacy Policies & Notices**
   □ Website privacy policy
   □ Mobile app privacy policy
   □ Employee privacy notice
   □ Cookie notice/banner
   □ Data processing agreements
   □ Consent forms (where required)

**3. Technical & Organizational Measures**
   □ Encryption (at rest and in transit)
   □ Access controls and authentication
   □ Logging and monitoring
   □ Incident response plan
   □ Vendor management program
   □ Employee training
   □ Regular security assessments

**4. Individual Rights Management**
   □ Request intake process
   □ Identity verification
   □ Response timelines
   □ Data subject request (DSR) workflow
   □ Deletion procedures
   □ Opt-out mechanisms

**5. Breach Response**
   □ Detection and containment
   □ Investigation and assessment
   □ Notification (authorities and individuals)
   □ Documentation and reporting
   □ Remediation and prevention

**Privacy Compliance Checklist:**
   □ Conduct privacy impact assessment
   □ Appoint privacy officer/DPO
   □ Create and publish privacy policy
   □ Implement cookie consent (if required)
   □ Establish data processing agreements
   □ Train employees on privacy
   □ Implement technical safeguards
   □ Create breach response plan
   □ Document compliance efforts
   □ Conduct regular audits

**Common Privacy Mistakes:**
   ⚠️ Collecting data without legal basis
   ⚠️ Inadequate privacy notices
   ⚠️ No vendor due diligence
   ⚠️ Excessive data retention
   ⚠️ Weak security measures
   ⚠️ No breach response plan
   ⚠️ Ignoring individual rights requests

**Next Steps:**
   1. Determine applicable regulations
   2. Conduct data inventory
   3. Gap analysis against requirements
   4. Develop privacy program
   5. Implement technical controls
   6. Train team and monitor compliance

---
*This is general information, not legal advice. Consult a privacy attorney and data protection expert.*
        """.strip()
    
    def _handle_business_formation(self, message: str) -> str:
        """Handle business formation and structure"""
        return f"""
🏢 **Business Formation & Structure**

**Request:** {message}

**Entity Types Comparison:**

**1. Sole Proprietorship**
   • **Pros:**
     - Simplest to form
     - Minimal paperwork
     - Complete control
     - Pass-through taxation
   
   • **Cons:**
     - Unlimited personal liability
     - Difficult to raise capital
     - Limited credibility
     - Ends with owner
   
   • **Best For:** Solo freelancers, low-risk businesses

**2. Partnership**
   • **General Partnership (GP)**
     - Unlimited personal liability for all partners
     - Pass-through taxation
     - Shared management
   
   • **Limited Partnership (LP)**
     - General partners: Unlimited liability
     - Limited partners: Liability limited to investment
     - Limited partners can't manage
   
   • **Best For:** Professional practices, real estate investments

**3. Limited Liability Company (LLC)**
   • **Pros:**
     - Limited liability protection
     - Pass-through taxation (default)
     - Flexible management structure
     - Fewer formalities than corporation
     - Can elect S-corp or C-corp taxation
   
   • **Cons:**
     - Self-employment tax on all income
     - State-specific rules vary
     - Less established for raising capital
   
   • **Formation:**
     - File Articles of Organization
     - Create Operating Agreement
     - Obtain EIN
     - State filing fee: $50-$500
   
   • **Best For:** Small businesses, startups, real estate

**4. C Corporation**
   • **Pros:**
     - Limited liability
     - Unlimited shareholders
     - Easy to raise capital
     - Perpetual existence
     - Stock options for employees
   
   • **Cons:**
     - Double taxation (corporate + dividend)
     - More formalities (board, meetings, minutes)
     - More expensive to maintain
     - Complex tax returns
   
   • **Formation:**
     - File Articles of Incorporation
     - Adopt Bylaws
     - Issue stock
     - Elect board of directors
     - Obtain EIN
     - State filing fee: $100-$800
   
   • **Best For:** High-growth startups seeking VC funding

**5. S Corporation**
   • **Pros:**
     - Limited liability
     - Pass-through taxation (no double tax)
     - Reasonable salary + distributions (tax savings)
     - Credibility with customers/vendors
   
   • **Cons:**
     - Restrictions: Max 100 shareholders, US residents only
     - One class of stock only
     - Strict formalities
     - Reasonable salary requirement
   
   • **Formation:**
     - Form C-corp first
     - File Form 2553 with IRS (within 75 days)
     - All shareholders must consent
   
   • **Best For:** Profitable small businesses, service companies

**6. Benefit Corporation (B-Corp)**
   • **Pros:**
     - Limited liability
     - Social mission protection
     - Attracts impact investors
     - Marketing advantage
   
   • **Cons:**
     - Annual benefit report required
     - Fiduciary duty to stakeholders (not just shareholders)
     - Not available in all states
   
   • **Best For:** Social enterprises, mission-driven companies

**Decision Matrix:**

| Factor | Sole Prop | LLC | S-Corp | C-Corp |
|--------|-----------|-----|--------|--------|
| Liability Protection | ❌ | ✅ | ✅ | ✅ |
| Ease of Formation | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Tax Efficiency | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Raising Capital | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Administrative Burden | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Formation Checklist:**

**Pre-Formation:**
   □ Choose business name (check availability)
   □ Determine entity type
   □ Select state of formation
   □ Identify registered agent
   □ Draft business plan

**Formation:**
   □ File formation documents with state
   □ Obtain EIN from IRS
   □ Open business bank account
   □ Create operating agreement/bylaws
   □ Issue membership interests/stock
   □ File beneficial ownership report (FinCEN)

**Post-Formation:**
   □ Obtain business licenses/permits
   □ Register for state taxes
   □ Set up accounting system
   □ Obtain business insurance
   □ File initial reports (if required)
   □ Establish corporate records

**Ongoing Compliance:**
   □ Annual reports/franchise tax
   □ Board meetings and minutes (corp)
   □ Tax returns (federal and state)
   □ Employment tax filings
   □ Maintain registered agent
   □ Update ownership records

**State Selection Considerations:**

**Delaware**
   • Pros: Business-friendly laws, Court of Chancery, privacy
   • Cons: Annual franchise tax, registered agent fee
   • Best for: VC-backed startups, large corporations

**Nevada**
   • Pros: No state income tax, privacy protections
   • Cons: Annual fees, not necessary for most businesses
   • Best for: Asset protection, privacy-focused

**Wyoming**
   • Pros: Low fees, no state income tax, strong LLC laws
   • Cons: Less established than Delaware
   • Best for: LLCs, holding companies

**Home State**
   • Pros: Simplest, lowest cost, local access
   • Cons: May have higher taxes or less favorable laws
   • Best for: Most small businesses

**Startup-Specific Considerations:**

**If Seeking VC Funding:**
   • Form Delaware C-Corporation
   • Implement equity incentive plan
   • Use standard VC documents (NVCA forms)
   • Clean cap table from day one
   • 83(b) elections for founders

**If Bootstrapping:**
   • LLC or S-Corp for tax efficiency
   • Operating agreement with vesting
   • Profit-sharing arrangements
   • Flexible ownership structure

**Cost Estimates:**

**DIY Formation:**
   • State filing fees: $50-$800
   • Registered agent: $100-300/year
   • EIN: Free
   • Total: $150-$1,100

**Attorney-Assisted:**
   • Legal fees: $1,000-$5,000
   • Plus state fees
   • Total: $1,500-$6,000

**Formation Services (LegalZoom, etc.):**
   • Service fee: $200-$500
   • Plus state fees
   • Total: $350-$1,300

**Recommended Actions:**
   1. Assess your specific needs and goals
   2. Consult with attorney and CPA
   3. Choose appropriate entity type
   4. File formation documents
   5. Implement corporate governance
   6. Maintain ongoing compliance

---
*This is general information, not legal advice. Consult a business attorney and tax advisor.*
        """.strip()
    
    def _general_legal_research(self, message: str) -> str:
        """Handle general legal research"""
        return f"""
⚖️ **Legal Research**

**Query:** {message}

**Legal Research Process:**

**1. Issue Identification**
   • Define the legal question
   • Identify relevant jurisdiction
   • Determine area of law
   • Note key facts

**2. Primary Sources**
   • **Statutes** - Federal and state codes
   • **Regulations** - Administrative rules (CFR, state regs)
   • **Case Law** - Court decisions
   • **Constitutional Law** - Federal and state constitutions

**3. Secondary Sources**
   • Legal encyclopedias (Am Jur, CJS)
   • Treatises and hornbooks
   • Law review articles
   • Restatements of Law
   • Practice guides

**4. Research Databases**
   • **Free Resources:**
     - Google Scholar (case law)
     - Cornell LII (statutes, regulations)
     - Justia (case law, statutes)
     - FindLaw (legal information)
   
   • **Paid Resources:**
     - Westlaw
     - LexisNexis
     - Bloomberg Law
     - Fastcase

**5. Citation Format (Bluebook)**
   • Cases: *Brown v. Board of Education*, 347 U.S. 483 (1954)
   • Statutes: 42 U.S.C. § 1983 (2018)
   • Regulations: 29 C.F.R. § 1630.2 (2020)

**Legal Research Tips:**
   ✓ Start broad, then narrow
   ✓ Update research (check if law has changed)
   ✓ Shepardize/KeyCite cases (verify still good law)
   ✓ Note circuit splits
   ✓ Consider policy arguments
   ✓ Document your research trail

**When to Consult an Attorney:**
   • Complex legal issues
   • High stakes matters
   • Litigation or disputes
   • Regulatory compliance
   • Contract negotiation
   • Business transactions

**Finding an Attorney:**
   • State bar referral service
   • Martindale-Hubbell
   • Avvo
   • LegalZoom attorney network
   • Personal referrals

**Questions to Ask:**
   • Experience in relevant area
   • Fee structure (hourly, flat, contingency)
   • Estimated costs
   • Timeline
   • Communication preferences

**Next Steps:**
   1. Clarify your specific legal question
   2. Gather relevant documents
   3. Conduct preliminary research
   4. Consult with attorney if needed
   5. Document findings and advice

---
*This is general information, not legal advice. Consult a licensed attorney for specific legal matters.*

**For detailed analysis of your specific situation, please provide:**
   • Jurisdiction (state/country)
   • Specific legal question
   • Relevant facts and documents
   • Timeline and urgency
   • Desired outcome
        """.strip()
    
    def extract_lesson(self, experience: Dict) -> str:
        """Learn from legal interactions"""
        task_type = experience.get("task_type", "general")
        success = experience.get("success", False)
        
        if success:
            return f"Successfully provided legal guidance on {task_type}"
        else:
            return f"Need to improve legal analysis for {task_type} matters"
