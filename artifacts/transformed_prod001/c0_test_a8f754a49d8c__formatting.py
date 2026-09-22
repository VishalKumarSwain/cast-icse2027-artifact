def plot_stacked_signals(
    x_or_y, y=None, draw_zero_lines=True, ax=None, sep=None, labels=None, **kwargs
):
    x, y = parse_plot_args(x_or_y, y)
    if y.ndim == 1:
        y = y[:, None]
    if sep is None:
        sep = np.abs(np.min(y)) + np.abs(np.max(y))
    if ax is None:
        ax = plt.gca()
    offsets = -np.arange(y.shape[1]) * sep
    y = y + offsets
    h = ax.plot(x, y, **kwargs)
    if labels is False:
        ax.tick_params(axis="y", labelleft="off")
    elif isinstance(labels, (list, tuple)):
        assert (
            len(labels) == y.shape[1]
        ), "Number of labels must match number of signals."
        ax.set_yticks(offsets)
        ax.set_yticklabels(labels)
    if draw_zero_lines:
        hz = axhlines(offsets, color="k", zorder=1.5)
    else:
        hz = None
    return h, hz
