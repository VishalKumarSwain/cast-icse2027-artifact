def copy_yaml_and_set_data_dirs(in_path, out_path, data_dir=None):
    from utime.hyperparameters import YAMLHParams
    hparams_renamed = YAMLHParams(in_path, no_log=True, no_version_control=True)
    data_ids = ("train", "val", "test")
    for dataset in data_ids:
        path = os.path.join(data_dir, dataset) if data_dir else "Null"
        dataset = dataset + "_data"
        if hparams_renamed.get(dataset) and not hparams_renamed[dataset].get("data_dir"):
            hparams_renamed.set_value(dataset, "data_dir", path, True, True)
    hparams_renamed.save_current(out_path)