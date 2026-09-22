def running(field):
    field = field.replace('H', '.')
    field = field.replace('C', '.')
    field = field.replace('R', '.')
    return field

def update_field(field, action):
    if action == 'eating':
        return eating(field)
    elif action == 'running':
        return running(field)
    else:
        return field

def main():
    field = "HCARV"
    def _extracted_0():
        print("Initial field: ", field)
        print("After eating: ", eating(field))
        print("After running: ", running(field))
        print("Update field (eating): ", update_field(field, 'eating'))
        print("Update field (running): ", update_field(field, 'running'))
    _extracted_0()

if __name__ == "__main__":
    main()
