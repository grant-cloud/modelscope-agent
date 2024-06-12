class CreateStoryError(Exception):
    def __init__(self, step):
        self.message = f"{step}: Story generation failure"
        super().__init__(self.message)

    def __str__(self):
        return f'{self.__class__.__name__}: {self.message}'


class BaseError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.__class__.__name__}: {self.message}'
