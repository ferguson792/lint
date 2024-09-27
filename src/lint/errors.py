class ConfigurationError(Exception):
    """
    This exception is raised when there is a configuration problem
    (e.g. an unknown value or configuration field).
    """
    pass

class ModelOutputError(RuntimeError):
    """
    This error occurs when the response of a model is wrong in some way.
    """
    pass
