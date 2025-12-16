# create and manage quizzes
class Quiz:
    def __init__(self):
        self.players = []
        self.questions = []
        self.question_count = 0
        self.answers = [] # answer is capital letter
        self.scoreboard = {} # player : score
        self.question_index = 0
        self.started = False
        self.player_answered = {} # player : true/false
        self.player_status = {} # player : correct/first/wrong
        self.first_taken = False # someone answered first and took all points

    def add_player(self, player_name):
        if self.players.count(player_name) > 0:
            return -1 # player already exists, shouldnt allow connection
        self.players.append(player_name)
        return 0

    def drop_player(self, player_name):
        if self.players.count(player_name) == 0:
            return -1 # player does not exist
        self.players.remove(player_name)
        return 0

    def set_qa(self, questions, answers):
        self.questions = questions
        self.answers = answers

    def start(self, question_count):
        self.question_count = question_count
        self.question_index = 0
        self.started = True
        self.first_taken = False
        for p in self.players:
            self.scoreboard[p] = 0
            self.player_answered[p] = False
            self.player_status[p] = '0'
    
    def next_question(self):
        self.question_index += 1
        if self.question_index >= self.question_count:
            return -1 # game should end

        self.first_taken = False
        for p in self.players:
            self.player_answered[p] = False
            self.player_status[p] = '0'
        return 0
    
    def give_answer(self, player_name, answer): # answer is capital letter
        if self.player_answered[player_name]:
            return -1 # you already answered dummy

        self.player_answered[player_name] = True # they are answering
        if answer == self.answers[self.question_index % len(self.answers)]: # correct answer, can loop
            if not self.first_taken: # bonus points, total equal to player count
                self.first_taken = True
                self.scoreboard[player_name] += len(self.players)
                self.player_status[p] = 'F' # first
            else:
                self.scoreboard[player_name] += 1
                self.player_status[p] = 'C' # correct
        else:
            self.player_status[p] = 'W' # wrong

        return 0

    def check_if_all_answered():
        count = 0
        for p in self.players: # only count players that are in the game
            if self.player_answered[p]:
                count += 1

        return count == len(self.players) # true if all players answered

    def scoreboard_printable(self):
        board = ""
        sorted_items = sorted(self.scoreboard.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

        rank = 1
        count = 1
        for item in sorted_items:
            board += f"{rank}. {item[0]}, with {item[1]} points\n"
            count += 1
            # only increase if no tie
            if count <= len(sorted_items) and item[1] > sorted_items[count-1][1]:
                rank = count

        return board

    def current_question_printable(self):
        return self.questions[self.question_index % len(self.questions)] # looping questions
        