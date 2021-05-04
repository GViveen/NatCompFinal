from os import name
import classes
import utils

def main():
    g = classes.Grid(32)
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