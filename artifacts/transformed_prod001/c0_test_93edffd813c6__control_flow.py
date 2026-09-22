def CALL_BASIC(routine, *args):
    the_subroutine = u2py.Subroutine(routine, len(args))
    cnt = 0
    for each in args:
        the_subroutine.args[cnt] = args[cnt]
        cnt += 1
    the_subroutine.call()
    out_args = []
    out_var = 0
    while out_var < cnt:
        thisDyn = the_subroutine.args[out_var]
        try:
            outValue = int(thisDyn)
        except ValueError:
            try:
                outValue = float(thisDyn)
            except ValueError:
                delim = thisDyn.count(u2py.FM) + thisDyn.count(u2py.VM) + thisDyn.count(u2py.SM)
                if delim == 0:
                    try:
                        outValue = str(thisDyn)
                    except ValueError:
                        outValue = thisDyn
                else:
                    outValue = thisDyn
        out_args.append(outValue)
        out_var += 1
    return out_args