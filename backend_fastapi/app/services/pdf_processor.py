import fitz


def extract_text(file_path: str) -> str:
    """
    Extract text from PDF document
    """

    document = fitz.open(file_path)

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    return text


def generate_summary(text: str) -> str:
    """
    Temporary summary generator.
    Later replace with AI model.
    """

    if not text:
        return "No text extracted"

    sentences = text.split(".")

    summary = ".".join(sentences[:5])

    return summary