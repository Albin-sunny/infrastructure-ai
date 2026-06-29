from backend.app.rag.recommendation import get_repair_recommendation
print(
    get_repair_recommendation(
        "Medium",
        10.22
    )
)