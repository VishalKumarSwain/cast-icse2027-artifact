def add_or_update_skill(skill_id):
    skill_list = ["skill_a", "skill_b", "skill_c"]

    # Check if the skill is already in the list
    if skill_id in skill_list:
        # Remove the existing skill
        skill_list.remove(skill_id)

    # Add the new skill to the front of the list
    skill_list.insert(0, skill_id)

    return skill_list
