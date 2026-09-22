def _eval_predictions(self):
        self._logger.info("Eval results with BOP toolkit ...")
        results_all = {f"iter{_i}": [] for _i in range(self.n_iter_test + 1)}
        refine_i = 0
        while refine_i < self.n_iter_test + 1:
            for pred in self._predictions:
                results_all[f"iter{refine_i}"].append(pred[f"iter{refine_i}"])
            refine_i += 1
        save_and_eval_results(self.cfg, results_all, self._output_dir, obj_ids=self.obj_ids)
        return {}