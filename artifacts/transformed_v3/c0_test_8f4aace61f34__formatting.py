def proj4StringToDictionary(proj4_string):
    proj4_dict = OrderedDict(re.findall("\+([^ ]+)=([^ ]+)", proj4_string))
    all_params = re.findall("\+([^ =]+)", proj4_string)
    for param in all_params:
        if param not in proj4_dict:
            proj4_dict[param] = None
    return proj4_dict
