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


class GMDNotInitialisedException(Exception):
    pass
