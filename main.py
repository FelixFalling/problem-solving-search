from problem_solving_as_search import n_problem


def main():
    board_config = [4, 5, "b", 6, 1, 8, 7, 3, 2]
    print("Hello from problem-solving-search!")
    my_problem = n_problem(8,board_config)
    my_problem.get_number_of_inversions()

if __name__ == "__main__":
    main()
