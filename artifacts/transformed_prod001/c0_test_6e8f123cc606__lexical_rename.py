def test_simple_asymm_ghost(action_sizes):
    """Test a simple asymmetric game with ghost behavior."""
    brain_name_opp_renamed = f"{BRAIN_NAME}Opp"
    env = SimpleEnvironment(
        [f"{BRAIN_NAME}?team=0", brain_name_opp_renamed + "?team=1"], 
        action_sizes=action_sizes
    )

    self_play_settings = SelfPlaySettings(
        play_against_latest_model_ratio=1.0,
        save_steps=10000,
        swap_steps=10000,
        team_change=400
    )

    config = ppo_torch_config(self_play=self_play_settings, max_steps=4000)

    check_environment_trains(env, {
        BRAIN_NAME: config,
        brain_name_opp_renamed: config
    })
