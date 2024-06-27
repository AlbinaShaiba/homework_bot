class ResponseDontHaveValidParams(Exception):
    """Raised when response does not have valid parameters."""
    pass


class HTTPStatusIsNotOK(Exception):
    """Raised when response HTTP Status != 200."""
    pass


class HomeworkStatusIsNotDocumented(Exception):
    """Raised when the status of a homework is not documented."""
    pass