from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


HttpMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
EndpointPurpose = Literal[
    "list_products",
    "list_vouchers",
    "list_categories",
    "list_combos",
    "get_config",
    "create_user",
    "create_order",
    "apply_voucher",
    "other_read",
    "other_write",
]


class EndpointConfig(BaseModel):
    id: str
    name: str
    method: HttpMethod
    url: str
    purpose: EndpointPurpose
    headers: dict[str, str] = Field(default_factory=dict)
    description: str = ""
    body_schema: Optional[dict[str, Any]] = None
    query_params: dict[str, str] = Field(default_factory=dict)


class BusinessConfig(BaseModel):
    name: str = ""
    business_type: str = ""
    description: str = ""
    open_date: str = ""
    location: str = ""
    base_url: str = ""
    notes: str = ""


class GrowthConfig(BaseModel):
    mode: Literal["day", "month", "year"] = "day"
    start_orders_per_day: int = 10
    monthly_growth_rate: float = 0.15
    plateau_at_month: int = 12
    new_user_ratio: float = 0.3


class SegmentState(BaseModel):
    id: str
    name: str
    description: str
    size: int
    weight: float
    personality_hints: list[str] = Field(default_factory=list)
    yesterday_orders: int = 0
    yesterday_revenue: float = 0.0
    yesterday_summary: str = ""
    top_products: list[str] = Field(default_factory=list)
    voucher_usage_rate: float = 0.0
    total_orders: int = 0
    total_revenue: float = 0.0


class SimulationState(BaseModel):
    current_day: int = 0
    growth_stage: Literal["pre_open", "early", "growing", "stable", "plateau"] = "pre_open"
    total_users_created: int = 0
    total_orders_created: int = 0
    total_revenue: float = 0.0
    last_run_at: Optional[str] = None
    segments: list[SegmentState] = Field(default_factory=list)


class RunLogEntry(BaseModel):
    timestamp: str
    day: int
    segment_id: Optional[str] = None
    action: str
    endpoint: Optional[str] = None
    status: Literal["ok", "error", "info"] = "info"
    detail: str = ""


class Memory(BaseModel):
    business: BusinessConfig = Field(default_factory=BusinessConfig)
    growth: GrowthConfig = Field(default_factory=GrowthConfig)
    endpoints: list[EndpointConfig] = Field(default_factory=list)
    snapshot: dict[str, Any] = Field(default_factory=dict)
    changes_from_last_run: list[str] = Field(default_factory=list)
    simulation: SimulationState = Field(default_factory=SimulationState)
    logs: list[RunLogEntry] = Field(default_factory=list)
    settings: dict[str, Any] = Field(default_factory=dict)
    # Runtime counters for the SQL sink (explicit-ID allocation, unique user seq)
    sql_sink: dict[str, Any] = Field(default_factory=dict)


class SyncResult(BaseModel):
    synced_endpoints: list[str]
    changes: list[str]
    errors: list[str]


class SimulateRequest(BaseModel):
    days: int = 1
    mode: Literal["day", "month", "year"] = "day"


class SimulateResult(BaseModel):
    days_simulated: int
    new_logs: list[RunLogEntry]
    final_day: int
