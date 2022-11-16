class BaseError(Exception):
    """Base rockps error. """


class ModelSaveError(BaseError):
    """ Wrong data in dict """


class AuthorizationError(BaseError):
    """Authorization error. """


class ServiceError(BaseError):
    """Any error that occurs on service's layer. """


class MailServiceError(ServiceError):
    """Mail (services.external.mail) service error. """


class MailServiceProviderResponseError(MailServiceError):
    """Invalid response from mail provider. """


class CallServiceError(ServiceError):
    """Call (services.external.call) service error. """
