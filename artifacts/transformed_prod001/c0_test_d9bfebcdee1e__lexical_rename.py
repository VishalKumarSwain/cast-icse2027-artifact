def is_iterative_turning(
        state: Tuple, momentum_sum: TensorVariable, momentum: TensorVariable
    ):
        momentum_ckpts, momentum_sum_ckpts, idx_min, idx_max = state
        def body_fn(i):
            subtree_momentum_sum_renamed = (
                momentum_sum - momentum_sum_ckpts[i] + momentum_ckpts[i]
            )
            is_turning = is_turning_fn(
                momentum_ckpts[i], momentum, subtree_momentum_sum_renamed
            )
            reached_max_iteration = at.lt(i - 1, idx_min)
            do_stop = at.any(is_turning | reached_max_iteration)
            return (i - 1, is_turning), until(do_stop)
        val, _ = aesara.scan(body_fn, outputs_info=(idx_max, None), n_steps=idx_max + 2)
        is_turning = val[1][-1]
        is_turning = at.where(
            at.lt(idx_max, idx_min), at.as_tensor(0, dtype="bool"), is_turning
        )
        return is_turning