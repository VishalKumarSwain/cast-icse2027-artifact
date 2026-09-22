def upload_status(correlation_id, is_success, status_code, status_description):
    if not isinstance(correlation_id, str):
        return {"return_code": "400", "message": "Correlation ID must be a string"}
    if not isinstance(is_success, bool):
        return {"return_code": "400", "message": "is_success must be a boolean"}
    if not isinstance(status_code, int):
        return {"return_code": "400", "message": "status_code must be an integer"}
    if not isinstance(status_description, str):
        return {"return_code": "400", "message": "status_description must be a string"}

    # processing goes here...

    return {"return_code": "200", "message": "Upload status processed successfully"}
