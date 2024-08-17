class UHDRError(Exception):
    def __init__(self, message):
        super().__init__(message)


class UHDRResizeError(UHDRError):
    def __init__(self, message):
        super().__init__(message)
