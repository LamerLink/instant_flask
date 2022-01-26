# Use this file to store local exceptions.

class AuthenticationFailureError(Exception):
    def __init__(
        self,
        msg: str = 'Failed to authenticate id with token.',
        *args,
        **kwargs
    ) -> None:
        super().__init__(msg,*args,**kwargs)
