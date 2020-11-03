from server.server import db
from server.models.user import User
from server.models.puzzle_exception import PuzzleException

MAX_PLAYERS_PER_PUZZLE = 4


class PuzzlePlayer(db.Model):

    __tablename__ = 'puzzle_players'

    player_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    puzzle_id = db.Column(db.Integer, db.ForeignKey('sudoku_puzzles.id'), primary_key=True)

    def __init__(self, player_id, puzzle_id):
        self.player_id = player_id
        self.puzzle_id = puzzle_id

    def save(self, autocommit=True):
        """
        Save a new puzzle-player paring to the database. Autocommit if specified.
        """
        db.session.add(self)

        if autocommit:
            db.session.commit()

    @classmethod
    def find_all_puzzles_for_player(cls, username):
        """
        Find all puzzles for a specific player based on the player's username.
        """
        user = User.find_by_username(username)
        return cls.query.filter_by(player_id=user.id).all()

    @classmethod
    def find_players_for_puzzle(cls, puzzle_id):
        """
        Returns a list of all users associated with a specific puzzle.
        """
        print("hello")
        return User.query\
            .join(PuzzlePlayer, PuzzlePlayer.player_id == User.id)\
            .filter_by(puzzle_id=puzzle_id)\
            .all()

    @classmethod
    def add_player_to_puzzle(cls, puzzle_id, username):
        if len(PuzzlePlayer.find_players_for_puzzle(puzzle_id)) > MAX_PLAYERS_PER_PUZZLE:
            raise PuzzleException(f"There are already {MAX_PLAYERS_PER_PUZZLE} "
                                  f"players affiliated with puzzle {puzzle_id}")

        user = User.find_by_username(username)
        puzzle_player = PuzzlePlayer(user.id, puzzle_id)
        puzzle_player.save(autocommit=True)

    def __str__(self):
        return f"PuzzlePlayer(player_id={self.player_id}, puzzle_id={self.puzzle_id})"

