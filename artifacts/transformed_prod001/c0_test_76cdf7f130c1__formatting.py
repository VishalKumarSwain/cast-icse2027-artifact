def _Simulate(
    self,
    test_data_generators,
    clean_capture_input_filepath,
    render_input_filepath,
    test_data_cache_path,
    echo_test_data_cache_path,
    output_path,
    config_filepath,
    echo_path_simulator,
):
    test_data_generators.Generate(
        input_signal_filepath=clean_capture_input_filepath,
        test_data_cache_path=test_data_cache_path,
        base_output_path=output_path,
    )
    apm_input_metadata = None
    try:
        apm_input_metadata = data_access.Metadata.LoadFileMetadata(
            clean_capture_input_filepath
        )
    except IOError as e:
        apm_input_metadata = {}
    apm_input_metadata["test_data_gen_name"] = test_data_generators.NAME
    apm_input_metadata["test_data_gen_config"] = None
    for config_name in test_data_generators.config_names:
        logging.info(" - test data generator config: <%s>", config_name)
        apm_input_metadata["test_data_gen_config"] = config_name
        noisy_capture_input_filepath = test_data_generators.noisy_signal_filepaths[
            config_name
        ]
        reference_signal_filepath = test_data_generators.reference_signal_filepaths[
            config_name
        ]
        evaluation_output_path = test_data_generators.apm_output_paths[config_name]
        echo_path_filepath = echo_path_simulator.Simulate(echo_test_data_cache_path)
        apm_input_filepath = input_mixer.ApmInputMixer.Mix(
            echo_test_data_cache_path, noisy_capture_input_filepath, echo_path_filepath
        )
        apm_input_basepath, apm_input_filename = os.path.split(apm_input_filepath)
        self._ExtractCaptureAnnotations(
            apm_input_filepath,
            apm_input_basepath,
            os.path.splitext(apm_input_filename)[0] + "-",
        )
        self._audioproc_wrapper.Run(
            config_filepath=config_filepath,
            capture_input_filepath=apm_input_filepath,
            render_input_filepath=render_input_filepath,
            output_path=evaluation_output_path,
        )
        try:
            self._evaluator.Run(
                evaluation_score_workers=self._evaluation_score_workers,
                apm_input_metadata=apm_input_metadata,
                apm_output_filepath=self._audioproc_wrapper.output_filepath,
                reference_input_filepath=reference_signal_filepath,
                output_path=evaluation_output_path,
            )
            data_access.Metadata.SaveAudioTestDataPaths(
                output_path=evaluation_output_path,
                clean_capture_input_filepath=clean_capture_input_filepath,
                echo_free_capture_filepath=noisy_capture_input_filepath,
                echo_filepath=echo_path_filepath,
                render_filepath=render_input_filepath,
                capture_filepath=apm_input_filepath,
                apm_output_filepath=self._audioproc_wrapper.output_filepath,
                apm_reference_filepath=reference_signal_filepath,
            )
        except exceptions.EvaluationScoreException as e:
            logging.warning("the evaluation failed: %s", e.message)
            continue
