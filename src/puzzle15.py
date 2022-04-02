import os
import numpy as np
import time
from heapq import heapify, heappop, heappush


class State:
    def __init__(self, board: np.ndarray, parent: 'State' = None, last_dir: tuple[int, int] = (0, 0)):
        # Inisialisasi state awal
        self.board = board
        self.parent = parent
        self.blank_index = np.where(self.board == 16)
        self.is_expanded = False
        self.children = []
        self.last_dir = last_dir

        # Mendapatkan kedalaman state dari state awal
        self.depth = 0 if parent is None else parent.depth + 1

        # Mendapatkan nilai cost dari state
        self.weight = self._calculate_weight()

        # Apakah state merupakan goal
        if self.weight == self.depth:
            self.is_goal = True
        else:
            self.is_goal = False

    def get_kurang(self) -> dict[int, int]:
        kurang = {}
        for i in range(4):
            for j in range(4):
                for key in kurang:
                    if key > self.board[i][j]:
                        kurang[key] += 1
                kurang[self.board[i][j]] = 0
        return kurang

    def _calculate_weight(self) -> int:
        # Menghitung nilai cost dari state
        heuristic = 0
        for i in range(4):
            for j in range(4):
                if self.board[i][j] != 4*i + j + 1 and self.board[i][j] != 16:
                    heuristic += 1
        return heuristic + self.depth

    def expand(self) -> None:
        # Expand state untuk mendapatkan semua state yang dapat dijalankan dari state
        if (self.is_expanded):
            # Jika state sudah di expand, maka tidak perlu di expand lagi
            return
        self.is_expanded = True

        # Seluruh arah yang memungkinkan selain arah sebelum
        directions = {(1, 0), (0, 1), (-1, 0), (0, -1)} - \
            {(self.last_dir[0] * -1, self.last_dir[1] * -1)}

        children = []
        for direction in directions:
            # Jika posisi blank tidak out of bounds jika ditambah dengan jarak, lewati
            if (self.blank_index[0] + direction[0]) < 0 or (self.blank_index[0] + direction[0]) > 3 or (self.blank_index[1] + direction[1]) < 0 or (self.blank_index[1] + direction[1]) > 3:
                continue
            new_board = self.board.copy()
            new_board[self.blank_index] = new_board[(
                self.blank_index[0] + direction[0], self.blank_index[1] + direction[1])]
            new_board[(self.blank_index[0] + direction[0],
                       self.blank_index[1] + direction[1])] = 16
            children.append(State(new_board, self, direction))
        self.children = children

    def __lt__(self, other):
        # Untuk mengurutkan state berdasarkan nilai cost
        return self.weight < other.weight

    def __str__(self):
        # Untuk menampilkan state
        return str(self.board)


class BNBTree:
    def __init__(self, root: State):
        # Inisialisasi state pohon awal
        self.root = root
        self.queue = []
        heappush(self.queue, (0, root))
        self.visited = set()
        self.solution = None
        self.search_time = None
        self.expanded_nodes_count = None
        self.route = []

    def is_solvable(self) -> bool:
        return (sum(self.root.get_kurang().values()) + (sum(self.root.blank_index) % 2)[0]) % 2 == 0

    def search(self) -> State:
        # Mencari solusi dari state awal

        # Jika tidak dapat di solve, maka tidak perlu dicari
        if not self.is_solvable():
            return None

        # Inisialisasi data pencarian
        self.search_time = 0
        self.expanded_nodes_count = 0
        start = time.time()
        cur_solution = None

        while self.queue:
            # Mencari state yang memiliki nilai cost terkecil
            state = heappop(self.queue)[1]

            # Jika sudah pernah dilalui, maka lewati
            if str(state) in self.visited:
                continue

            # Tandai sudah pernah dlilalui
            self.visited.add(str(state))

            # Jika state merupakan goal, maka lakukan pruning dan simpan solusi sekarang
            if state.is_goal:
                for i in range(len(self.queue) - 1, -1, -1):
                    if (self.queue[i][1].weight > state.weight):
                        self.queue.pop(i)
                cur_solution = state
                continue

            # Jika state belum merupakan goal, maka expand state
            state.expand()
            self.expanded_nodes_count += 1

            # Masukkan semua anak state yang sudah di expand ke dalam queue
            for child in state.children:
                if (str(child) not in self.visited) and (child.weight < cur_solution.weight if cur_solution is not None else True):
                    heappush(self.queue, (child.weight, child))

        # Selesaikan pencarian
        self.search_time = time.time() - start
        state = cur_solution
        self.solution = state

        # Mendapatkan jalur dari solusi
        self.route = []
        self.route.append(self.solution)
        while state.parent is not None:
            self.route.append(state.parent)
            state = state.parent
        self.route.append(state)

        # Mengembalikan solusi
        return self.solution
