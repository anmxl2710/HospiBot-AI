def parse_task(text):

    text = text.lower()

    if "icu" in text:
        return "ICU", 10

    elif "ward" in text:
        return "WARD", 5

    elif "pharmacy" in text:
        return "PHARMACY", 15

    else:
        return "GENERAL", 0
