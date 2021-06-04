from os import name
import utils

from simulation_classes import Grid
from evo_classes import Population

def main(use_simulated_data=False, create_new_file=False, num_generations=1000):
    data_file = ""
    if use_simulated_data:
        data_file = "./data/complex_test.in"
        if create_new_file:
            g = Grid(100, simple_scenario=False)
            g.gen_hashcode_string(
                duration=700,
                num_cars=100,
                hops=12,
                bonus_points=1000,
                save=True,
                name='complex_test.in',
                min_neighbors=3,
                max_neighbors=100
            )
    else:
        data_file = "./data/hashcode.in"
    sim, intersection_dict = utils.create_default_sim_from_file(data_file)
    pop = Population(sim, intersection_dict, \
        gen_size=100, candidate_size=100, timing_cap=10, \
        mutation_rate=0.001, tournament_size=5)
    b, w, m = pop.run(num_generations)
    print(f"Generation {num_generations} - best: {b}, worst: {w}, mean: {m}")
    
    return 0


if __name__ == "__main__":
    main(use_simulated_data=True, create_new_file=False, num_generations=10000)