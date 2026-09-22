def running(field_renamed):
    field_renamed = field_renamed.replace('H', '.')
    field_renamed = field_renamed.replace('C', '.')
    field_renamed = field_renamed.replace('R', '.')
    return field_renamed

def update_field(field_renamed, action):
    if action == 'eating':
        return eating(field_renamed)
    elif action == 'running':
        return running(field_renamed)
    else:
        return field_renamed

def main():
    field_renamed = "HCARV"
    print("Initial field: ", field_renamed)
    print("After eating: ", eating(field_renamed))
    print("After running: ", running(field_renamed))
    print("Update field (eating): ", update_field(field_renamed, 'eating'))
    print("Update field (running): ", update_field(field_renamed, 'running'))

if __name__ == "__main__":
    main()
