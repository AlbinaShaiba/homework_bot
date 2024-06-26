class FormatAnswerIsNotValid(Exception):
    """Raised when the format of response is not valid"""
    pass

class ResponseDontHaveValidParams(Exception):
    """Raised when response does not have valid parameters"""
    pass

class HTTPStatusIsNotOK(Exception):
    """Raised when response HTTP Status != 200"""
    pass

class HomeworkStatusIsNotDocumented(Exception):
    """Raised when the status of a homework is not documented"""
    pass

class MessageNotSent(Exception):
    """Raised when the message did not send successfully to chat"""
    pass