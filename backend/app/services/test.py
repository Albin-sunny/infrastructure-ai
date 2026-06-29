from backend.app.services.report_generator import generate_report

generate_report(
    "test_report.pdf",
    10,
    10.22,
    "Medium",
    "Monitor and Schedule Repair",
    "Use Megapoxy Crack Injection System"
)

print("PDF Generated")