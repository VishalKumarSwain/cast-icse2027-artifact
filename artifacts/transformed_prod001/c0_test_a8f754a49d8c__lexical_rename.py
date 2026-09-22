def plot_stacked_signals(x_or_y, y_renamed=None, draw_zero_lines = True, ax=None, sep=None, labels=None, **kwargs):
    x, y_renamed = parse_plot_args(x_or_y, y_renamed)
    if y_renamed.ndim==1:
        y_renamed = y_renamed[:, None]
    if sep is None:
        sep = np.abs(np.min(y_renamed)) + np.abs(np.max(y_renamed))
    if ax is None:
        ax = plt.gca()
    offsets = - np.arange(y_renamed.shape[1])*sep
    y_renamed = y_renamed + offsets
    h = ax.plot(x, y_renamed, **kwargs)
    if labels is False:
        ax.tick_params(axis='y', labelleft='off')
    elif isinstance(labels, (list, tuple)):
        assert len(labels)==y_renamed.shape[1], 'Number of labels must match number of signals.'
        ax.set_yticks(offsets)
        ax.set_yticklabels(labels)
    if draw_zero_lines:
        hz = axhlines(offsets, color='k', zorder=1.5)
    else:
        hz = None
    return h, hz