"""
File is currently WIP / deprecated weil kack ansatz.
"""

#
# class Question:
#     questions = []
#
#     def __init__(self, key=None, value_type=None, choices=None, default_value=None, current_value=None,
#                  relevant_platform=[]):
#         self.key = key
#         self.current_value = current_value
#         self.value_type = value_type
#         self.choices = choices
#         self.default_value = default_value
#         self.relevant_platform = relevant_platform
#         self.questions.append(self)
#
#     def __repr__(self):
#         return f"Question {self.key}, {self.current_value=},{self.value_type=}, {self.choices=}, {self.default_value=}"
#
#     def get_database_value(self, team: Team):
#         return team.value_of_setting(self.key)
#
#
# Question(key="WEEKLY_OP_LINK", value_type=bool, choices=[True, False], default_value=True, )
# Question(key="PIN_WEEKLY_OP_LINK", value_type=bool, choices=[True, False], default_value=True, )
# Question(key="LINEUP_NOTIFICATION", value_type=bool, choices=[True, False], default_value=True, )
# Question(key="TEAM_SCHEDULING_SUGGESTION", value_type=bool, choices=[True, False], default_value=True, )
# Question(key="SCHEDULING_CONFIRMATION", value_type=bool, choices=[True, False], default_value=True, )
# Question(key="SCOUTING_WEBSITE", value_type=str, default_value="op.gg", choices=["op.gg", "u.gg", "xdx.gg"])
# # Question(key="FAV_ANIMAL", value_type=list, default_value="dog", choices=["cat", "dog", ])
#
# # Question(key="TEAM_SCHEDULING_SUGGESTION", value_type=bool, choices=[True, False], default_value=True, )
#
# print(Question.questions)
