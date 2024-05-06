from copy import deepcopy
import random
from math import log, sqrt


class Node:
    def __init__(self, game_state, parent=None, move=None):
        self.game_state = deepcopy(game_state)
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = game_state.generate_possible_moves()

    def select_child(self):
        return max(self.children, key=lambda x: x.wins / x.visits + sqrt(2 * log(x.parent.visits) / x.visits))

    def expand(self):
        move = self.untried_moves.pop()
        new_state = deepcopy(self.game_state)
        new_state.make_move(*move)
        child_node = Node(new_state, parent=self, move=move)
        self.children.append(child_node)
        return child_node

    def simulate(self):
      simulation_state = deepcopy(self.game_state)
      move_count = 0
      while simulation_state.generate_possible_moves() and move_count < 50:  
        possible_moves = simulation_state.generate_possible_moves()
        move = random.choice(possible_moves)
        simulation_state.make_move(*move)
        move_count += 1
      return simulation_state.check_for_winner()


    def update(self, result):
        self.visits += 1
        if result == self.game_state.current_player:
            self.wins += 1
        if self.parent:
            self.parent.update(result)

    def mcts(self, iterations):
        for _ in range(iterations):
            node = self
            # Selection
            while node.untried_moves == [] and node.children != []:
                node = node.select_child()
            # Expansion
            if node.untried_moves:
                node = node.expand()
            # Simulation
            result = node.simulate()
            # Backpropagation
            node.update(result)
        return max(self.children, key=lambda x: x.visits).move


class CheckersGame:
    def __init__(self):
        self.board = [[' ' for _ in range(8)] for _ in range(8)]
        self.current_player = 'W'  

    def initialize_board(self):
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 != 0:
                    if row < 3:
                        self.board[row][col] = 'W'
                    elif row > 4:
                        self.board[row][col] = 'B'

    def print_board(self):
        print("   " + "   ".join(str(i) for i in range(8)))
        print("  +" + "---+" * 8)
        for index, row in enumerate(self.board):
            print(f"{index} | " + " | ".join(row) + " |")
            print("  +" + "---+" * 8)
        print()

    def is_valid_move(self, start_row, start_col, end_row, end_col):
      if not (0 <= start_row < 8 and 0 <= start_col < 8 and 0 <= end_row < 8 and 0 <= end_col < 8):
        return False
      if self.board[end_row][end_col] != ' ':
        return False
      if self.board[start_row][start_col] not in {'W', 'B'}:
        return False

      piece = self.board[start_row][start_col]
      row_diff = end_row - start_row
      col_diff = abs(end_col - start_col)

      # Check direction of the move based on the piece color
      if (piece == 'B' and row_diff >= 0) or (piece == 'W' and row_diff <= 0):
        return False  

      if abs(row_diff) == 1 and col_diff == 1:
        return True  
      elif abs(row_diff) == 2 and col_diff == 2:
        middle_row = (start_row + end_row) // 2
        middle_col = (start_col + end_col) // 2
        opponent = 'W' if piece == 'B' else 'B'
        if self.board[middle_row][middle_col] == opponent:
            return True 

      return False



    def generate_possible_moves(self):
      captures = []
      regular_moves = []
      for row in range(8):
        for col in range(8):
            if self.board[row][col] == self.current_player:
                if self.current_player == 'B':
                    # B moves only upward (negative row index direction)
                    directions = [(-1, -1), (-1, 1)]
                else:
                    # W moves only downward (positive row index direction)
                    directions = [(1, -1), (1, 1)]

                for d in directions:
                    target_row, target_col = row + d[0], col + d[1]
                    if 0 <= target_row < 8 and 0 <= target_col < 8 and self.board[target_row][target_col] == ' ':
                        regular_moves.append((row, col, target_row, target_col))
                    jump_row, jump_col = row + 2 * d[0], col + 2 * d[1]
                    if 0 <= jump_row < 8 and 0 <= jump_col < 8 and self.board[jump_row][jump_col] == ' ':
                        if self.board[target_row][target_col] != ' ' and self.board[target_row][target_col] != self.current_player:
                            captures.append((row, col, jump_row, jump_col))
      return captures if captures else regular_moves



    def make_move(self, start_row, start_col, end_row, end_col):
        self.board[end_row][end_col] = self.board[start_row][start_col]
        self.board[start_row][start_col] = ' '
        if abs(start_row - end_row) == 2:
            middle_row = (start_row + end_row) // 2
            middle_col = (start_col + end_col) // 2
            self.board[middle_row][middle_col] = ' '

    def switch_player(self):
        self.current_player = 'B' if self.current_player == 'W' else 'W'

    def check_for_winner(self):
      white_count = sum(row.count('W') for row in self.board)
      black_count = sum(row.count('B') for row in self.board)
      if white_count == 0 or black_count == 0:
        return 'W' if black_count == 0 else 'B'
      return None 


    def play(self):
      self.initialize_board()
      while True:
        self.print_board()
        print(f"Current player: {self.current_player}")

        moves = self.generate_possible_moves()
        if not moves:
            print(f"No valid moves available for {self.current_player}.")
            other_player = 'B' if self.current_player == 'W' else 'W'
            self.current_player = other_player  # Switch to the other player to check moves
            if not self.generate_possible_moves():  # Check if the other player also has no moves
                print(f"No valid moves available for {self.current_player} either.")
                print("Game ends in a draw.")
                break
            else:
                print(f"{other_player} wins! No valid moves left for {self.current_player}.")
                break

        if self.current_player == 'W':
            valid_move_made = False
            while not valid_move_made:
                try:
                    start_row, start_col = map(int, input("Enter start position (row col): ").split())
                    end_row, end_col = map(int, input("Enter end position (row col): ").split())
                    if self.is_valid_move(start_row, start_col, end_row, end_col):
                        self.make_move(start_row, start_col, end_row, end_col)
                        valid_move_made = True
                    else:
                        print("Invalid move. Try again.")
                except ValueError:
                    print("Please enter valid integer coordinates.")
        else:  # AI player
            print("AI is making a move...")
            self.ai_move()

        winner = self.check_for_winner()
        if winner:
            print(f"{winner} wins!")
            break

        self.switch_player()



    def ai_move(self):
      moves = self.generate_possible_moves()
      if not moves:
        print("No valid moves available for AI.")
        return
    
      if len(moves) > 8:
        print("Using MCTS due to a large number of possible moves.")
        root_node = Node(self, None, None)
        best_move = root_node.mcts(1000)
      else:
        print("Using Minimax for deeper strategic analysis.")
        best_move, _ = self.minimax(self, 3)

      if best_move:
        self.make_move(*best_move)
        print(f"AI moves from ({best_move[0]}, {best_move[1]}) to ({best_move[2]}, {best_move[3]})")
      else:
        print("AI has no moves to play.")


    def evaluate_board(self):
      white_count = sum(row.count('W') for row in self.board)
      black_count = sum(row.count('B') for row in self.board)
      if self.current_player == 'W':
        return white_count - black_count
      else:
        return black_count - white_count


    def minimax(self, state, depth, maximizing_player=True):
      if depth == 0 or not state.generate_possible_moves():
        return None, state.evaluate_board()

      best_move = None
      if maximizing_player:
        max_eval = float('-inf')
        for move in state.generate_possible_moves():
            new_state = deepcopy(state)
            new_state.make_move(*move)
            _, eval = self.minimax(new_state, depth - 1, False)
            if eval > max_eval:
                max_eval = eval
                best_move = move
        return best_move, max_eval
      else:
        min_eval = float('inf')
        for move in state.generate_possible_moves():
            new_state = deepcopy(state)
            new_state.make_move(*move)
            _, eval = self.minimax(new_state, depth - 1, True)
            if eval < min_eval:
                min_eval = eval
                best_move = move
        return best_move, min_eval


if __name__ == "__main__":
    game = CheckersGame()
    game.play()
