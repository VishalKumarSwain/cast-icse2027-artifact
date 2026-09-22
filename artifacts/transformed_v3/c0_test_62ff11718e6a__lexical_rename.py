def letter_to_future_self():
    future_date_renamed = "October 2028"
    hopes_and_dreams = {
        "career": "To have advanced my career in AI/ML, perhaps in a leadership role, contributing significantly to impactful projects.",
        "personal_growth": "To have continued my personal development, learning new skills, and exploring other areas of interest.",
        "health": "To maintain a balanced lifestyle, focusing on both physical and mental well-being.",
        "relationships": "To have nurtured my relationships with family and friends, creating a supportive network.",
        "hobbies": "To pursue hobbies and passions that bring me joy and fulfillment outside of work."
    }

    letter = f"Dear Future Me,\n\n"
    letter += f"As I sit down to write this letter on the brink of the next five years, I want to outline my hopes and dreams for {future_date_renamed}:\n\n"
    
    for area, dream in hopes_and_dreams.items():
        letter += f"- In my career, I hope: {dream}\n"

    letter += "\nI hope this letter finds you well and that you have accomplished many of these aspirations. Remember to stay true to yourself and embrace the journey ahead.\n\n"
    letter += "Best Wishes,\nYour Past Self"

    return letter

if __name__ == "__main__":
    print(letter_to_future_self())
