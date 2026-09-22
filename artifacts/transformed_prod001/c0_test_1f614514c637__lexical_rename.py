def add_or_update_skill(skill_id):
    skill_list_renamed = ['skill_a', 'skill_b', 'skill_c']

    # Check if the skill is already in the list
    if skill_id in skill_list_renamed:
        # Remove the existing skill
        skill_list_renamed.remove(skill_id)

    # Add the new skill to the front of the list
    skill_list_renamed.insert(0, skill_id)

    return skill_list_renamed
