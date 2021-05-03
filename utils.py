# -*- coding: utf-8 -*-
"""
Created on Sat May  1 08:10:36 2021

@author: Glenn
"""

from collections import defaultdict
from classes import Simulation

def parse_input(filename):
    # Create dict to hold streets
    street_dict = defaultdict(tuple)
    # Create list to hold all paths
    paths = []
    
    # Read in file
    with open(filename, 'r') as f:
        content = f.readlines()
        
    # Parse first line to extract sim parameters
    parameters = list(map(int, content[0].split()))
    
    D = parameters[0] # number of iterations in simulation
    # I = parameters[1] # number of intersections
    S = parameters[2] # number of streets
    # V = parameters[3] # number of vehicles
    F = parameters[4] # score per vehicle getting to destination
    
    # Parse street info
    for line in content[1:1+S]:
        # Parse line elements
        l = line.split()
        to = int(l[1])
        name = l[2]
        length = int(l[3])
        
        # Store information in dicts
        street_dict[name] = (to, length)
        
    # Parse path info
    for line in content[1+S:]:
        # Parse line elements
        l = line.split()
        paths.append(l[1:])
    
    return street_dict, paths, D, F

def create_default_sim_from_file(filename):
    S, P, D, F = parse_input(filename)
    sim = Simulation(S, P, F, D)
    
    return sim