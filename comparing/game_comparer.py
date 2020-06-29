class Comparer:

    def __init__(self, game_old, game_new):
        self.game_old = game_old
        self.game_new = game_new

    def compare_new_suggestion_of_enemy(self):
        if len(self.game_old.suggestion_logs) < len(self.game_new.suggestion_logs) and \
                len(self.game_new.suggestion_logs) > 0 and self.game_new.suggestion_logs[0].name \
                not in TEAM_LEADER:
            return True
        return False

    def compare_new_suggestion_of_our_team(self):
        if len(self.game_old.suggestion_logs) < len(self.game_new.suggestion_logs) and \
                len(self.game_new.suggestion_logs) > 0 and self.game_new.suggestion_logs[0].name \
                in TEAM_LEADER:
            return True
        return False

    def compare_scheduling_confirmation(self):
        old_log = self.game_old.get_scheduling_confirmation_log()
        new_log = self.game_new.get_scheduling_confirmation_log()
        if new_log is not None and old_log is None:
            return True
        return False

    def compare_lineup_confirmation(self):
        link_old = self.game_old.create_op_link_of_enemy_lineup()
        link_new = self.game_new.create_op_link_of_enemy_lineup()
        return True if link_old is None and link_new is not None else False
