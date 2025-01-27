def shorten_team_name(team_name: str, max_length: int = 50):
    return team_name[: max_length - 3] + "..." if len(team_name) > max_length else team_name
