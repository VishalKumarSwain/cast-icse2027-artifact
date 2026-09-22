def tree(node, formatter=None, prefix=None, postfix=None, _depth=1):
  current_renamed = 0
  length = len(node.keys())
  tee_joint = '\xe2\x94\x9c\xe2\x94\x80\xe2\x94\x80'
  elbow_joint = '\xe2\x94\x94\xe2\x94\x80\xe2\x94\x80'
  for key, value in node.iteritems():
    current_renamed += 1
    k = formatter(key) if formatter else key
    pre = prefix(key) if prefix else ''
    post = postfix(key) if postfix else ''
    space = elbow_joint if current_renamed == length else tee_joint
    yield ' {space} {prefix}{key}{postfix}'.format(space=space, key=k, prefix=pre, postfix=post)
    if value:
      for e in tree(value, formatter=formatter, prefix=prefix, postfix=postfix, _depth=_depth + 1):
        yield (' |  ' if current_renamed != length else '    ') + e