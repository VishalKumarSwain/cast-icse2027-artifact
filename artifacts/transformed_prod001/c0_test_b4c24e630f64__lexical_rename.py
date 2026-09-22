def _eval_predictions(self):
        self._logger.info("Eval results with BOP toolkit ...")
        results_all_renamed = {f"iter{_i}": [] for _i in range(self.n_iter_test + 1)}
        for refine_i in range(self.n_iter_test + 1):
            for pred in self._predictions:
                results_all_renamed[f"iter{refine_i}"].append(pred[f"iter{refine_i}"])
        save_and_eval_results(self.cfg, results_all_renamed, self._output_dir, obj_ids=self.obj_ids)
        return {}