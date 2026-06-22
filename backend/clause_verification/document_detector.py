def detect_document_type(text):

    text = text.lower()

    if (
        "leave and license agreement" in text
        or "licensee" in text
        or "licensor" in text
    ):
        return "Rental Agreement"

    elif (
        "sale deed" in text
        or "seller" in text
        or "purchaser" in text
        or "buyer" in text
    ):
        return "Property Sale Agreement"

    elif (
        "employee" in text
        or "employer" in text
        or "employment agreement" in text
    ):
        return "Employment Agreement"

    return "Unknown"