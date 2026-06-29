from backend.app.rag.generate_answer import generate_answer


def get_repair_recommendation(
    severity,
    crack_area_percent
):

    query = f"""
    A concrete crack was detected.

    Severity: {severity}
    Crack Area Percentage: {crack_area_percent}

    Based on the repair manual:

    - Recommend a repair method
    - Mention materials required
    - Give a short explanation
    """

    return generate_answer(query)