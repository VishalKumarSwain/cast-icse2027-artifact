def analyze(self, q=(0.025, 0.5, 0.975)):
        formula_covar_renamed = np.cov(self.formulas, rowvar=False)
        functional_covar = np.cov(self.functional_groups, rowvar=False)
        formula_q = np.quantile(self.formulas, q, axis=0)
        functional_q = np.quantile(self.functional_groups, q, axis=0)
        results = {
            "formula": {"covariance": formula_covar_renamed, "quantile": formula_q},
            "functional": {"covariance": functional_covar, "quantile": functional_q}
        }
        fig = go.Figure()
        for index, atom in enumerate(["H", "C", "O", "N"]):
            fig.add_trace(
                go.Violin(
                    x=[atom,] * len(self.formulas),
                    y=self.formulas[atom],
                    name=atom,
                    meanline_visible=True,
                    opacity=0.6,
                )
            )
        fig.update_layout(title_text="Predicted formula", xaxis_title="Atom", yaxis_title="Number")
        return fig, results