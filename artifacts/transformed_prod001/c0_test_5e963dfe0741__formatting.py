def take_snapshot(file_list):
    if type(file_list) == str:
        file_str = file_list
    elif type(file_list) == list:
        file_str = file_list[0].ljust(len(file_list[0]) + 1)
        for i in range(1, len(file_list)):
            file_str += file_list[i].ljust(len(file_list[i]) + 1)
        file_str = file_str[:-1]
    try:
        os.system(f"vmd -dispdev text -e render_snapshot.vmd -args {file_str}")
    except:
        print("VMD is required to use this function")
