# create and manage quizzes
class quiz:
    def __init__(self):
        self.players = []
        self.questions = []
        self.question_count = 0
        self.answers = []
        self.scoreboard = {} # player : score
        self.question_index = 0
        self.started = False

    def add_player(player_name):
        if self.players.count(player_name) > 0:
            return -1 # player already exists, shouldnt allow connection
        self.players.append(player_name)
        return 0

    def drop_player(player_name):
        if self.players.count(player_name) == 0:
            return -1 # player does not exist
        self.players.remove(player_name)
        return 0

    def set_qa(questions, answers):
        self.questions = questions
        self.answers = answers

    def start(question_count):
        self.question_count = question_count
        self.started = True
        for p in self.players:
            self.scoreboard[p] = 0
