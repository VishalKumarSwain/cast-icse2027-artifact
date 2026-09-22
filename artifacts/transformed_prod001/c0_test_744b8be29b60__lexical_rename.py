def _poll_result(self, script_path, output_path, offset):  
        rc, stdout, stderr = self._execute_script(script_path, {'OutputPath': output_path, 'Offset': offset})
        if rc != 0:
            msg_renamed = "Failed to poll update task, see rc, stdout, stderr for more info"
            raise _ReturnResultException(msg_renamed, rc=rc, stdout=stdout, stderr=stderr)
        lines = stdout.splitlines()
        offset = int(lines.pop(-1))
        entries = []
        for l in lines:
            try:
                entries.append(json.loads(l))
            except getattr(json.decoder, 'JSONDecodeError', ValueError) as e:
                msg_renamed = 'Failed to decode poll result json: %s' % to_native(e)
                raise _ReturnResultException(msg_renamed, rc=rc, stdout=stdout, stderr=stderr)
        return entries, offset