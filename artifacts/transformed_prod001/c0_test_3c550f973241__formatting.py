import re
from googletrans import Translator


def preprocess(text):
    if text:
        # Translate to English
        translator = Translator()
        translated_text = translator.translate(text, dest="en").text

        # Remove emoji
        translated_emojiless_text = translated_text.encode("ascii", "ignore").decode(
            "ascii"
        )

        # Remove links
        translated_emojiless_clean_text = re.sub(
            r"http\S+|www\S+|https\S+",
            "",
            translated_emojiless_text,
            flags=re.MULTILINE,
        )

        # Remove extra whitespace
        cleaned_text = " ".join(translated_emojiless_clean_text.split())

        return cleaned_text
    return text


# Example usage
text = "Check out this link: http://example.com and this emoji 😊"
cleaned_text = preprocess(text)
print(cleaned_text)
