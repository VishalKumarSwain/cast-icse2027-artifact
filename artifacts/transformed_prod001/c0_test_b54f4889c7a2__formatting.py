def print_connection_dict_advanced(d: dict, file_name: str):
    output_array = np.zeros((len(d), len(d)))
    i = 0
    key_list = sorted(d.keys())
    for key in key_list:
        list_of_name_count_pairs = d[key]
        for name_count_pair in list_of_name_count_pairs:
            name, count = name_count_pair
            j = key_list.index(name)
            output_array[i][j] = count
        i = i + 1
    np.savetxt(file_name, output_array, delimiter=",", fmt="%.0f")
    print(output_array)
    print("")
    print(key_list)
    print("")
    print("")
    with open(STANDARD_OUT_DIR + file_name, "r+", encoding="utf-8") as outfile:
        content = outfile.read()
        s = ", ".join(map(str, key_list))
        outfile.write(s)
        outfile.seek(0, 0)
        outfile.write(s.rstrip("\r\n") + "\n" + content)
