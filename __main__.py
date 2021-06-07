from os import name
import utils
import argparse

from simulation_classes import Grid
from evo_classes import Population


def main(
    use_simulated_data=False,
    create_new_file=False,
    num_generations=1000,
    gen_size=100,
    candidate_size=200,
    timing_cap=10,
    mutation_rate=0.001,
    tournament_size=5,
    fig_title="Default Run",
    replace=False,
    mutation_mode="schedule"
):
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
                name="complex_test.in",
                min_neighbors=3,
                max_neighbors=100,
            )
    else:
        data_file = "./data/hashcode.in"
    sim, intersection_dict = utils.create_default_sim_from_file(data_file)
    pop = Population(
        sim,
        intersection_dict,
        gen_size=gen_size,
        candidate_size=candidate_size,
        timing_cap=timing_cap,
        mutation_rate=mutation_rate,
        tournament_size=tournament_size,
        replace_parents=replace,
    )
    b, w, m = pop.run(num_generations)
    utils.plot_evolutionary_run(b, w, m, fig_title=fig_title)

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evolutionary Algorithm to solve traffic singalling problem"
    )
    parser.add_argument(
        "--use_hashcode",
        dest="hashcode",
        action="store_true",
        help="When True, the algorithm will use original hashcode data to build simulation.",
    )
    parser.set_defaults(hashcode=False)
    parser.add_argument(
        "--new_file",
        dest="new_file",
        action="store_true",
        help="When True, a new simulation file will be generated.",
    )
    parser.set_defaults(new_file=False)
    parser.add_argument(
        "--replace",
        dest="replace",
        action="store_true",
        help="If True, replace all parents every generation. If False, choose top n from among children + parents",
    )
    parser.set_defaults(replace=False)
    parser.add_argument(
        "--num_gens",
        dest="num_gens",
        default=100,
        type=int,
        help="Defines the number of generations the algorithm will run.",
    )
    parser.add_argument(
        "--gen_size",
        dest="gen_size",
        default=100,
        type=int,
        help="How many individuals in each generation.",
    )
    parser.add_argument(
        "--candidate_size",
        dest="candidate_size",
        default=200,
        type=int,
        help="How many individuals are generated in each generation.",
    )
    parser.add_argument(
        "--timing_cap",
        dest="timing_cap",
        default=10,
        type=int,
        help="Maximum number of consecutive iterations a single light can be green.",
    )
    parser.add_argument(
        "--mutation_rate",
        dest="muta_rate",
        default=0.001,
        type=float,
        help="Chance for each schedule of an individual to mutate during one reproduction cycle.",
    )
    parser.add_argument(
        "--tournament_size",
        dest="tour_size",
        default=5,
        type=int,
        help="How large are the tournaments in a tournament selection.",
    )
    parser.add_argument(
        "--fig_title", dest="fig_title", default="default run", type=str
    )
    parser.add_argument("--mutation_mode", dest="mut_mode", default="schedule", type=str, help="string controlling the mode of mutation. Needs to be either 'schedule' or 'individual'.")

    args = parser.parse_args()

    main(
        use_simulated_data=not (args.hashcode),
        create_new_file=args.new_file,
        num_generations=args.num_gens,
        gen_size=args.gen_size,
        candidate_size=args.candidate_size,
        timing_cap=args.timing_cap,
        mutation_rate=args.muta_rate,
        tournament_size=args.tour_size,
        replace=args.replace,
        fig_title=args.fig_title,
    )
