# Outbound message templates for grocery operations

KITCHEN_ALERT_TEMPLATE = (
    "⚠️ KITCHEN ALERT: {title}\n"
    "Severity: {severity}\n"
    "Description: {description}\n"
    "Recommended Action: {action}\n"
)

WEEKLY_REPORT_NOTIFICATION = (
    "📊 WEEKLY GROCERY SUMMARY\n"
    "Hello {family_name},\n"
    "Your weekly kitchen analytics and replenishment plan is ready.\n"
    "Total spent: ${weekly_spend:.2f}\n"
    "Low stock items count: {low_stock_count}\n"
    "Please check the downloadable report for details."
)
