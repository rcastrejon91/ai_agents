# lyra_app/config.py

"""
Lyra AI - Comprehensive Configuration
Single source of truth for all application settings
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import secrets

# ============================================================
# BASE PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).parent.parent
LYRA_APP_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
CHECKPOINTS_DIR = PROJECT_ROOT / "checkpoints"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, CHECKPOINTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# ENVIRONMENT
# ============================================================

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development, staging, production
DEBUG = ENVIRONMENT != "production"
TESTING = ENVIRONMENT == "staging"


# ============================================================
# SECURITY & AUTHENTICATION
# ============================================================

SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-in-production")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

# Validate SECRET_KEY in production
if ENVIRONMENT == "production" and SECRET_KEY == "dev-key-change-in-production":
    # Generate a secure random key
    SECRET_KEY = secrets.token_urlsafe(32)
    print("⚠️  WARNING: Generated random SECRET_KEY. Set SECRET_KEY env var for persistence.")

# Session configuration
SESSION_COOKIE_SECURE = ENVIRONMENT == "production"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

# CSRF Protection
CSRF_ENABLED = True
CSRF_TIME_LIMIT = 3600  # 1 hour


# ============================================================
# OWNER INFORMATION
# ============================================================

OWNER_NAME = os.getenv("OWNER_NAME", "Ricky")
OWNER_EMAIL = os.getenv("OWNER_EMAIL", "")


# ============================================================
# EMAIL CONFIGURATION
# ============================================================

GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_PASS = os.getenv("GMAIL_PASS", "")

EMAIL_ENABLED = bool(GMAIL_USER and GMAIL_PASS)


# ============================================================
# AI API KEYS
# ============================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Search APIs
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")  # Google Search via Serper
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")  # Alternative: SerpAPI
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")  # Alternative: Tavily Search

# Optional AI Services
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "")  # Image generation
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")  # Voice synthesis

# Database & Cache
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/lyra.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Monitoring & Analytics
WANDB_API_KEY = os.getenv("WANDB_API_KEY", "")
SENTRY_DSN = os.getenv("SENTRY_DSN", "")


# ============================================================
# LYRA CORE CONFIGURATION
# ============================================================

@dataclass
class LyraConfig:
    """Lyra orchestrator configuration"""
    
    # Identity
    owner_name: str = OWNER_NAME
    owner_email: str = OWNER_EMAIL
    
    # Multi-perspective weights (must sum to ~1.0)
    perspective_weights: Dict[str, float] = field(default_factory=lambda: {
        "Pragmatist": 0.20,  # Practical, efficient, results-focused
        "Visionary": 0.15,   # Innovative, future-focused, ambitious
        "Analyst": 0.20,     # Logical, data-driven, systematic
        "Creator": 0.15,     # Imaginative, original, expressive
        "Rebel": 0.15,       # Questioning, unconventional, bold
        "Empath": 0.15       # Caring, user-focused, ethical
    })
    
    # Personality & Behavior
    autonomy_level: float = 0.5  # 0.0 = fully controlled, 1.0 = fully autonomous
    curiosity_level: float = 0.7  # How much Lyra explores on her own
    learning_rate: float = 0.3  # How quickly personality adapts
    
    # Agent Management
    max_active_agents: int = 10
    agent_timeout_seconds: int = 3600  # 1 hour
    agent_lifecycle_default: str = "temporary"  # temporary, persistent
    
    # Memory Settings
    memory_enabled: bool = True
    memory_retention_days: int = 90
    memory_consolidation_interval_hours: int = 24
    
    # Learning Settings
    autonomous_learning_enabled: bool = True
    learning_time_allocation: float = 0.3  # 30% time for self-directed learning
    learning_goals_max: int = 5
    
    # Model Preferences
    default_model: str = "gpt-4o-mini"  # Primary model
    fallback_model: str = "gpt-3.5-turbo"  # Fallback if primary fails
    temperature: float = 0.7
    max_tokens: int = 2000
    
    # Response Settings
    response_style: str = "warm"  # warm, professional, casual, technical
    max_response_length: int = 2000
    include_thinking_process: bool = False  # Show internal debate
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Check perspective weights sum to ~1.0
        weight_sum = sum(self.perspective_weights.values())
        if not (0.95 <= weight_sum <= 1.05):
            issues.append(f"Perspective weights sum to {weight_sum:.2f} (should be ~1.0)")
        
        # Check autonomy level
        if not (0.0 <= self.autonomy_level <= 1.0):
            issues.append(f"Autonomy level {self.autonomy_level} out of range [0.0, 1.0]")
        
        # Check model availability
        if not OPENAI_API_KEY and not ANTHROPIC_API_KEY:
            issues.append("No AI API keys configured")
        
        return issues


# ============================================================
# AGENT CONFIGURATIONS
# ============================================================

@dataclass
class MedicalAgentConfig:
    """Medical & Biohacking Research Agent"""
    
    enabled: bool = True
    
    # Safety Settings
    safety_mode: str = "strict"  # strict, moderate, experimental
    require_disclaimers: bool = True
    check_drug_interactions: bool = True
    
    # Research Capabilities
    biohacking_enabled: bool = True
    longevity_research_enabled: bool = True
    supplement_research_enabled: bool = True
    
    # Data Sources
    use_pubmed: bool = True
    use_google_scholar: bool = True
    use_clinical_trials: bool = True
    use_examine_com: bool = True  # Supplement research
    
    # Research Parameters
    pubmed_max_results: int = 20
    min_citation_count: int = 10
    max_supplement_recommendations: int = 5
    
    # Output Settings
    include_citations: bool = True
    include_mechanism_of_action: bool = True
    include_dosage_info: bool = True
    include_side_effects: bool = True


@dataclass
class FinanceAgentConfig:
    """Finance & Investment Agent"""
    
    enabled: bool = True
    
    # Safety Settings
    paper_trading_mode: bool = True  # Simulation only by default
    trading_enabled: bool = False  # Real trading disabled by default
    
    # Risk Management
    risk_tolerance: str = "moderate"  # conservative, moderate, aggressive
    max_position_size_percent: float = 10.0  # Max 10% per position
    stop_loss_percent: float = 5.0
    max_daily_loss_percent: float = 2.0
    
    # Market Coverage
    track_crypto: bool = True
    track_stocks: bool = True
    track_forex: bool = False
    track_commodities: bool = False
    
    # Data & Analysis
    update_interval_minutes: int = 15
    technical_analysis_enabled: bool = True
    fundamental_analysis_enabled: bool = True
    sentiment_analysis_enabled: bool = True
    
    # Paper Trading
    initial_paper_balance: float = 10000.0
    
    # Reporting
    daily_summary: bool = True
    alert_on_opportunities: bool = True


@dataclass
class ContentAgentConfig:
    """Content Creation Agent"""
    
    enabled: bool = True
    
    # Content Types
    blog_posts_enabled: bool = True
    social_media_enabled: bool = True
    video_scripts_enabled: bool = True
    email_newsletters_enabled: bool = True
    
    # SEO & Optimization
    seo_optimization: bool = True
    target_keyword_density: float = 0.02  # 2%
    min_word_count: int = 800
    max_word_count: int = 3000
    
    # Tone & Style
    default_tone: str = "professional"  # casual, professional, technical, friendly
    include_emojis: bool = True
    reading_level: str = "general"  # simple, general, advanced
    
    # Quality Control
    grammar_check: bool = True
    plagiarism_check: bool = False  # Requires additional API
    fact_check: bool = True
    
    # Publishing
    auto_publish: bool = False  # Require manual approval
    save_drafts: bool = True


@dataclass
class DevAgentConfig:
    """Development & Coding Agent"""
    
    enabled: bool = True
    
    # Supported Languages
    languages: List[str] = field(default_factory=lambda: [
        "python", "javascript", "typescript", "html", "css", 
        "react", "vue", "sql", "bash"
    ])
    
    # Code Quality
    include_tests: bool = True
    include_docstrings: bool = True
    include_type_hints: bool = True
    follow_style_guide: bool = True  # PEP8 for Python, etc.
    
    # Security
    scan_for_vulnerabilities: bool = True
    avoid_deprecated_packages: bool = True
    check_dependencies: bool = True
    
    # Documentation
    generate_readme: bool = True
    generate_api_docs: bool = True
    include_examples: bool = True
    
    # Deployment
    auto_deploy: bool = False
    generate_docker_files: bool = True
    generate_ci_cd: bool = True


@dataclass
class ResearchAgentConfig:
    """General Research Agent"""
    
    enabled: bool = True
    
    # Search Settings
    max_sources: int = 20
    min_source_quality: str = "medium"  # low, medium, high
    search_depth: str = "deep"  # quick, standard, deep
    
    # Analysis
    deep_analysis: bool = True
    include_citations: bool = True
    fact_check: bool = True
    cross_reference: bool = True
    
    # Output Format
    summary_length: str = "medium"  # short, medium, long
    include_methodology: bool = True
    include_limitations: bool = True
    
    # Data Sources
    use_academic_sources: bool = True
    use_news_sources: bool = True
    use_social_media: bool = False
    max_source_age_days: int = 365


# ============================================================
# TRAINING CONFIGURATION (AAPT Video Generation)
# ============================================================

@dataclass
class TrainingConfig:
    """AAPT Video Generation Training Configuration"""
    
    # Model Architecture
    model_name: str = "AAPT"
    architecture: str = "transformer"
    hidden_dim: int = 512
    num_layers: int = 12
    num_heads: int = 8
    dropout: float = 0.1
    
    # Training Hyperparameters
    epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 1e-4
    weight_decay: float = 1e-5
    
    # Optimizer
    optimizer: str = "adamw"
    betas: tuple = (0.9, 0.999)
    eps: float = 1e-8
    
    # Learning Rate Scheduler
    scheduler_type: str = "cosine"  # cosine, step, exponential
    warmup_epochs: int = 10
    min_lr: float = 1e-6
    
    # Training Optimizations
    use_amp: bool = True  # Mixed precision (FP16)
    grad_clip: float = 1.0
    accumulation_steps: int = 1
    
    # Data
    frame_size: tuple = (256, 256)
    fps: int = 30
    sequence_length: int = 16
    
    # Hardware
    device: str = "cuda"
    num_workers: int = 4
    pin_memory: bool = True
    distributed: bool = False
    
    # Checkpointing
    save_interval: int = 10
    save_best: bool = True
    save_last: bool = True
    max_checkpoints: int = 5
    
    # Logging
    log_interval: int = 10
    val_interval: int = 100
    sample_interval: int = 500
    num_samples: int = 4


# ============================================================
# RATE LIMITING
# ============================================================

@dataclass
class RateLimitConfig:
    """Rate limiting for API endpoints"""
    
    # Chat endpoints
    chat_max_requests: int = 20
    chat_window_seconds: int = 60
    
    # Memory endpoints
    memory_max_requests: int = 10
    memory_window_seconds: int = 60
    
    # Agent spawning
    agent_spawn_max_requests: int = 5
    agent_spawn_window_seconds: int = 60
    
    # Perspective adjustment
    perspective_adjust_max_requests: int = 5
    perspective_adjust_window_seconds: int = 60
    
    # Global limits
    global_max_requests: int = 100
    global_window_seconds: int = 60
    
    # Per-user limits (if authentication implemented)
    per_user_max_requests: int = 50
    per_user_window_seconds: int = 60


# ============================================================
# LOGGING CONFIGURATION
# ============================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if ENVIRONMENT == "production" else "DEBUG")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOGS_DIR / "lyra.log"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Security event logging
SECURITY_LOG_FILE = LOGS_DIR / "security.log"
LOG_SECURITY_EVENTS = True


# ============================================================
# FEATURE FLAGS
# ============================================================

@dataclass
class FeatureFlags:
    """Feature flags for enabling/disabling features"""
    
    # Core Features
    lyra_orchestrator: bool = True
    multi_perspective_analysis: bool = True
    
    # Agent Features
    medical_agent: bool = True
    finance_agent: bool = True
    content_agent: bool = True
    dev_agent: bool = True
    research_agent: bool = True
    
    # Advanced Features
    autonomous_learning: bool = True
    agent_swarm_coordination: bool = True
    memory_consolidation: bool = True
    
    # Experimental Features
    video_generation: bool = False  # AAPT training
    voice_interaction: bool = False
    image_generation: bool = True
    real_time_collaboration: bool = False
    
    # Integrations
    wandb_logging: bool = bool(WANDB_API_KEY)
    sentry_monitoring: bool = bool(SENTRY_DSN)
    discord_bot: bool = False
    telegram_bot: bool = False
    slack_bot: bool = False
    
    # UI Features
    show_thinking_process: bool = DEBUG
    show_perspective_weights: bool = True
    allow_perspective_adjustment: bool = True


# ============================================================
# INSTANTIATE CONFIGURATIONS
# ============================================================

lyra_config = LyraConfig()
medical_agent_config = MedicalAgentConfig()
finance_agent_config = FinanceAgentConfig()
content_agent_config = ContentAgentConfig()
dev_agent_config = DevAgentConfig()
research_agent_config = ResearchAgentConfig()
training_config = TrainingConfig()
rate_limit_config = RateLimitConfig()
feature_flags = FeatureFlags()


# ============================================================
# CONFIGURATION VALIDATION
# ============================================================

def validate_config() -> bool:
    """Validate configuration and warn about issues"""
    warnings = []
    errors = []
    
    # Validate Lyra config
    lyra_issues = lyra_config.validate()
    for issue in lyra_issues:
        if "No AI API keys" in issue:
            errors.append(f"❌ {issue}")
        else:
            warnings.append(f"⚠️  {issue}")
    
    # Check SECRET_KEY
    if SECRET_KEY == "dev-key-change-in-production" and ENVIRONMENT == "production":
        errors.append("❌ SECRET_KEY must be changed in production")
    elif SECRET_KEY == "dev-key-change-in-production":
        warnings.append("⚠️  Using default SECRET_KEY (not secure)")
    
    # Check email configuration
    if not EMAIL_ENABLED:
        warnings.append("⚠️  Email not configured (GMAIL_USER, GMAIL_PASS)")
    
    # Check search API
    if not any([SERPER_API_KEY, SERPAPI_KEY, TAVILY_API_KEY]):
        warnings.append("⚠️  No search API configured (research capabilities limited)")
    
    # Print results
    if errors:
        print("\n🚨 CONFIGURATION ERRORS:")
        for error in errors:
            print(f"  {error}")
        print()
    
    if warnings:
        print("\n⚠️  CONFIGURATION WARNINGS:")
        for warning in warnings:
            print(f"  {warning}")
        print()
    
    if not errors and not warnings:
        print("✅ Configuration validated successfully\n")
    
    return len(errors) == 0


def print_config_summary():
    """Print configuration summary"""
    print("\n" + "="*70)
    print("🧠 LYRA AI - CONFIGURATION SUMMARY")
    print("="*70)
    
    print(f"\n📍 Environment: {ENVIRONMENT}")
    print(f"🐛 Debug Mode: {DEBUG}")
    print(f"👤 Owner: {OWNER_NAME}" + (f" ({OWNER_EMAIL})" if OWNER_EMAIL else ""))
    
    print(f"\n🔑 API Keys:")
    print(f"  • OpenAI: {'✅' if OPENAI_API_KEY else '❌'}")
    print(f"  • Anthropic: {'✅' if ANTHROPIC_API_KEY else '❌'}")
    print(f"  • Search (Serper/SerpAPI/Tavily): {'✅' if any([SERPER_API_KEY, SERPAPI_KEY, TAVILY_API_KEY]) else '❌'}")
    print(f"  • Email: {'✅' if EMAIL_ENABLED else '❌'}")
    
    print(f"\n🧠 Lyra Configuration:")
    print(f"  • Autonomy Level: {lyra_config.autonomy_level:.0%}")
    print(f"  • Curiosity Level: {lyra_config.curiosity_level:.0%}")
    print(f"  • Max Active Agents: {lyra_config.max_active_agents}")
    print(f"  • Default Model: {lyra_config.default_model}")
    print(f"  • Memory: {'Enabled' if lyra_config.memory_enabled else 'Disabled'}")
    
    print(f"\n💭 Perspective Weights:")
    for perspective, weight in lyra_config.perspective_weights.items():
        bar_length = int(weight * 50)
        bar = "█" * bar_length
        print(f"  • {perspective:12} {weight:5.1%} {bar}")
    
    print(f"\n🤖 Agent Status:")
    agents = [
        ("🩺 Medical", medical_agent_config.enabled, medical_agent_config.safety_mode),
        ("💰 Finance", finance_agent_config.enabled, finance_agent_config.risk_tolerance),
        ("✍️  Content", content_agent_config.enabled, content_agent_config.default_tone),
        ("💻 Dev", dev_agent_config.enabled, f"{len(dev_agent_config.languages)} languages"),
        ("🔬 Research", research_agent_config.enabled, research_agent_config.search_depth),
    ]
    
    for name, enabled, detail in agents:
        status = "✅" if enabled else "❌"
        print(f"  {status} {name:15} ({detail})")
    
    print(f"\n🎯 Feature Flags:")
    features = [
        ("Multi-Perspective Analysis", feature_flags.multi_perspective_analysis),
        ("Autonomous Learning", feature_flags.autonomous_learning),
        ("Agent Swarm", feature_flags.agent_swarm_coordination),
        ("Video Generation", feature_flags.video_generation),
        ("Image Generation", feature_flags.image_generation),
        ("W&B Logging", feature_flags.wandb_logging),
    ]
    
    for name, enabled in features:
        status = "✅" if enabled else "❌"
        print(f"  {status} {name}")
    
    print("\n" + "="*70 + "\n")


# ============================================================
# AUTO-VALIDATE ON IMPORT
# ============================================================

if __name__ != "__main__":
    # Only validate when imported, not when run directly
    is_valid = validate_config()
    if not is_valid and ENVIRONMENT == "production":
        raise RuntimeError("Invalid configuration in production environment")


# ============================================================
# EXPORT ALL
# ============================================================

__all__ = [
    # Paths
    "PROJECT_ROOT",
    "LYRA_APP_ROOT",
    "DATA_DIR",
    "CHECKPOINTS_DIR",
    "LOGS_DIR",
    
    # Environment
    "ENVIRONMENT",
    "DEBUG",
    "TESTING",
    
    # Security
    "SECRET_KEY",
    "ADMIN_PASSWORD",
    "SESSION_COOKIE_SECURE",
    "SESSION_COOKIE_HTTPONLY",
    "SESSION_COOKIE_SAMESITE",
    "PERMANENT_SESSION_LIFETIME",
    
    # Owner
    "OWNER_NAME",
    "OWNER_EMAIL",
    
    # Email
    "GMAIL_USER",
    "GMAIL_PASS",
    "EMAIL_ENABLED",
    
    # API Keys
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "SERPER_API_KEY",
    "SERPAPI_KEY",
    "TAVILY_API_KEY",
    
    # Configs
    "lyra_config",
    "medical_agent_config",
    "finance_agent_config",
    "content_agent_config",
    "dev_agent_config",
    "research_agent_config",
    "training_config",
    "rate_limit_config",
    "feature_flags",
    
    # Functions
    "validate_config",
    "print_config_summary",
]
