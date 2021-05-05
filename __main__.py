from os import name
from simulation_classes import Grid

def main():
    g = Grid(32)
    g.gen_hashcode_string(
        duration=700,
        num_cars=100,
        hops=12,
        bonus_points=1000,
        save=True,
        name='test.in'
    )

if __name__ == "__main__":
    main()