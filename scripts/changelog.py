# TODO refactor to github releases
def main():
    pass
    # teams = Team.objects.get_registered_teams()
    # for team in teams:
    #     try:
    #         print(team)
    #         dispatcher = MessageDispatcher(team)
    #         raw_message = pattern.format(team=team, version=log["version"])
    #         msg = NotificationToTeamMessage(team=team, custom_message=raw_message)
    #         dispatcher.dispatch_raw_message(msg=msg)
    #     except Exception as e:
    #         print(e)


def run():
    main()
