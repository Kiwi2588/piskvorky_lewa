import numpy as np

class ConvEnginePZ:
    def __init__(self):
        self.v_engine = "0.0.2"
        self.board = None
        self.player_symbol = 1   # By default, assume we are 'X' represented by 1
        self.opponent_symbol = -1  # Opponent is 'O' represented by -1
        self.initialize_parameters()

    def initialize_parameters(self):
        # One simple convolutional filter 3x3, one output channel
        self.parameters = {
            'conv_filter': np.random.randn(3,3) * 0.01,
            'W_out': np.random.randn(1, 9) * 0.01,  # after flattening the conv output
            'b_out': np.zeros((1,1))
        }

    def set_player_symbols(self, player_symbol=1, opponent_symbol=-1):
        """
        Set which symbol is used by the engine and which by the opponent.
        Typically:
          - player_symbol = 1 (X)
          - opponent_symbol = -1 (O)
        """
        self.player_symbol = player_symbol
        self.opponent_symbol = opponent_symbol

    def mutate(self, mutation_rate=0.1, mutation_scale=0.1):
        for key in self.parameters:
            mutation_mask = np.random.rand(*self.parameters[key].shape) < mutation_rate
            self.parameters[key] += np.random.randn(*self.parameters[key].shape) * mutation_scale * mutation_mask

    def evaluation(self):
        # 1. Original convolution-based evaluation
        patch = self.board[1:4,1:4]  # center 3x3 patch
        conv_out = np.sum(patch * self.parameters['conv_filter'])  # single value

        flat_input = patch.reshape(-1,1)
        Z = np.dot(self.parameters['W_out'], flat_input) + self.parameters['b_out']
        base_score = Z[0,0] + conv_out

        # 2. Additional blocking heuristic:
        #    Penalize states where opponent is about to win.
        #    Check all winning lines (3 rows, 3 cols, 2 diagonals).
        
        # Extract the 3x3 board region (assuming the full board is board[0:3,0:3]):
        full_board = self.board[0:3, 0:3]

        # All possible lines: 3 rows, 3 columns, 2 diagonals
        lines = []
        # Rows
        for i in range(3):
            lines.append(full_board[i, :])
        # Columns
        for j in range(3):
            lines.append(full_board[:, j])
        # Diagonals
        lines.append(np.array([full_board[0,0], full_board[1,1], full_board[2,2]]))
        lines.append(np.array([full_board[0,2], full_board[1,1], full_board[2,0]]))

        # Identify if the opponent is about to win:
        # Condition: exactly two opponent symbols and one empty cell in a line.
        opponent_threat_penalty = 0
        for line in lines:
            # Count symbols in the line
            opp_count = np.sum(line == self.opponent_symbol)
            empty_count = np.sum(line == 0)

            if opp_count == 2 and empty_count == 1:
                # This is a huge threat we should block ASAP
                opponent_threat_penalty -= 10.0

        # Combine both evaluations
        final_score = base_score + opponent_threat_penalty
        return final_score

    def evaluate_board(self, board):
        self.board = board.copy()
        return self.evaluation()

    def get_parameters(self):
        return {k: v.copy() for k,v in self.parameters.items()}

    def set_parameters(self, parameters):
        if isinstance(parameters, np.lib.npyio.NpzFile):
            parameters = {key: parameters[key] for key in parameters.files}
        self.parameters = {k: v.copy() for k,v in parameters.items()}

    def load_params(self, file=""):
        self.set_parameters(np.load(file))
