REQUIRED_COLUMNS = ["date", "product_id", "product_name", "quantity"]
OPTIONAL_COLUMNS = ["category", "price", "revenue", "promotion", "supplier", "lead_time", "inventory"]

RISK_CRITICAL = "Critical"
RISK_HIGH = "High"
RISK_MEDIUM = "Medium"
RISK_LOW = "Low"

HEALTH_HEALTHY = "Healthy"
HEALTH_WATCH = "Watch"
HEALTH_AT_RISK = "At Risk"
HEALTH_CRITICAL = "Critical"

RISK_COLORS = {
    HEALTH_HEALTHY: "#2ecc71",
    HEALTH_WATCH: "#f1c40f",
    HEALTH_AT_RISK: "#e67e22",
    HEALTH_CRITICAL: "#e74c3c",
}
