class CouldNotParseURLException(Exception):
    pass


class PrimeLeagueConnectionException(Exception):
    def __init__(self, msg=None, status_code=None, ):
        msg = msg or ""
        if status_code:
            msg += f"(Statuscode: {status_code})"
        super(PrimeLeagueConnectionException, self).__init__(msg)


class TeamWebsite404Exception(PrimeLeagueConnectionException):
    pass


class Match404Exception(PrimeLeagueConnectionException):
    pass


class PrimeLeagueParseException(PrimeLeagueConnectionException):
    pass


class Div1orDiv2TeamException(Exception):
    pass


class UnauthorizedException(PrimeLeagueConnectionException):
    def __init__(self):
        msg = (
            "You can only use the local file storage in development. "
            "See README.md 'Alternative to API' for further information."
        )
        print(msg)
        super().__init__(msg)


class VariableNotSetException(Exception):
    def __init__(self, variable_name):
        msg = (
            f"Environment variable '{variable_name}' not set. Did you setup the .env correctly?"
        )
        super().__init__(msg)
