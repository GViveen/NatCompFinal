from os import name
from simulation_classes import Grid


def main():
    # g = Grid(32,simple_scenario=True)
    # g.gen_hashcode_string(
    #     duration=700,
    #     num_cars=100,
    #     hops=12,
    #     bonus_points=1000,
    #     save=True,
    #     name='test.in'
    # )

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

if __name__ == "__main__":
    main()