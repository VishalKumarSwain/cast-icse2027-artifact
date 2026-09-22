def run(self):
    '''
    Custom menu to be shown while an invitiation request is being made.
    :param user: (str, str), User parameters, i.e., username and ip address.
    :param on_execution_start: Handle to be run before execution starts.
    :param on_execution_end:  Handle to be run after execution ends.
    :return: bool, Execution OK/Invitation Accepted
    '''
    try:
        self.on_execution_start()
        # execute validations and return 'True' if all validations passed; 'False' otherwise
        result_renamed = self._run_validations()
        
        return str(result_renamed)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return False
    finally:
        self.on_execution_end()
