from os import name
from simulation_classes import Grid
import utils


def main(use_simulated_data=False, create_new_file=False, num_generations=1000):
    data_file = ""
    if use_simulated_data:
        data_file = "./data/complex_test.in"
        if create_new_file:
            g = Grid(800, simple_scenario=False)
            hashcode_string = g.gen_hashcode_string(
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
    pop = utils.create_population_from_file(data_file, 0.1, gen_size=2)
    b, w, m = pop.run(num_generations)
    print(f"Generation {num_generations} - best: {b}, worst: {w}, mean: {m}")
    
    return 0

if __name__ == "__main__":
    main(use_simulated_data=True, create_new_file=False, num_generations=10000)