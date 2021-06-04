# -*- coding: utf-8 -*-
"""
Created on Sat May  1 08:10:36 2021

@author: Glenn
"""

from collections import defaultdict
from simulation_classes import Simulation
from evo_classes import Population
import matplotlib.pyplot as plt


def parse_input(filename):
    # Create dict to hold streets
    street_dict = defaultdict(tuple)
    # Create list to hold all paths
    paths = []
    # Create dict to hold all intersections for crossover purposes
    intersection_dict = defaultdict(list)

    # Read in file
    with open(filename, "r") as f:
        content = f.readlines()

    # Parse first line to extract sim parameters
    parameters = list(map(int, content[0].split()))

    D = parameters[0]  # number of iterations in simulation
    # I = parameters[1] # number of intersections
    S = parameters[2]  # number of streets
    # V = parameters[3] # number of vehicles
    F = parameters[4]  # score per vehicle getting to destination

    # Parse street info
    for line in content[1 : 1 + S]:
        # Parse line elements
        l = line.split()
        fr = int(l[0])
        to = int(l[1])
        name = l[2]
        length = int(l[3])

        # Store information in dicts
        street_dict[name] = (to, length)
        if not (fr in intersection_dict[to]):
            intersection_dict[to].append(fr)
            intersection_dict[fr].append(to)

    # Parse path info
    for line in content[1 + S :]:
        # Parse line elements
        l = line.split()
        paths.append(l[1:])

    return street_dict, paths, D, F, intersection_dict


def create_default_sim_from_file(filename):
    S, P, D, F, I = parse_input(filename)
    sim = Simulation(S, P, F, D)

    return sim, I


def create_population_from_file(filename):
    sim, inter_dict = create_default_sim_from_file(filename)
    pop = Population(sim, inter_dict)

    return pop


def plot_evolutionary_run(
    best,
    worst,
    mean,
    fig_no=1,
    fig_title="Performance of individuals across all generations.",
):
    plt.figure(fig_no)
    plt.plot(best, "r-", label="Best")
    plt.plot(worst, "b-", label="Worst")
    plt.plot(mean, "g-", label="Mean")
    plt.xlabel("Generation number")
    plt.ylabel("Score")
    plt.title(fig_title)
    plt.legend()
    plt.show()
