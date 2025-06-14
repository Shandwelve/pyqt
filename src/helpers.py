def replace_romanian_months(text: str) -> str:
    month_map = {
        "ianuarie": "january",
        "februarie": "february",
        "martie": "march",
        "aprilie": "april",
        "mai": "may",
        "iunie": "june",
        "iulie": "july",
        "august": "august",
        "septembrie": "september",
        "octombrie": "october",
        "noiembrie": "november",
        "decembrie": "december",
    }

    for ro, en in month_map.items():
        text = text.replace(ro, en)

    return text
