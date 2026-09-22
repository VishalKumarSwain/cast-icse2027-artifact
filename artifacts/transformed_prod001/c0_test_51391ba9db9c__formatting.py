self.assertEqual(len(tfds_episodes), len(md_episodes))

_DETERMINISTIC_CONFIG = """
task_def.dataset.seed = 20210917
task_def.episode_sampler.seed = 20210917
"""
