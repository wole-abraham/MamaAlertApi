class DomainError(Exception):
    """Base class for all domain errrors"""
    pass

class NotFoundError(DomainError):
    def __init__(self, message:str = "Resource not Found"):
        self.message = message

class ConflictError(DomainError):
    def __init__(self, message: str = "Conflict"):
        self.message = message

class ValidationError(DomainError):
    def __init__(self, message:str="Invalid input"):
        self.message = message

class UnauthorizedError(DomainError):
    def __init__(self, message: str = "Unauthorized"):
        self.message = message
    
class ServiceUnavailableError(DomainError):
    def __init__(self, message: str = "Servoce Unavailable"):
        self.message = message