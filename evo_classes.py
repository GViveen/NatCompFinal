# -*- coding: utf-8 -*-
"""
Created on Wed May  5 12:52:40 2021

@author: Glenn
"""

from numpy.random import default_rng
import numpy as np
from collections import defaultdict, deque
from tqdm import trange

class Individual:
    
    def __init__(self, schedules, mutation_rate = 0.001, timing_cap = 10):
        """
        Class to hold a single unit of evolution in the EA.
        Stores all schedules for a simulation as a dict and allows for self-mutation and deep-copying.
        Stores its own fitness.

        Parameters
        ----------
        schedules : dict
            dictionary using intersection identifiers as keys and a list of integers representing
            timings as values.
        mutation_rate : float, optional
            Chance for the schedule of every intersection to mutate. The default is 0.001.
        timing_cap : integer, optional
            Defines the maximum amount of iterations a certain light is allowed 
            to stay green before cycling. The default is 10.

        """
        self.schedules = schedules
        self.mutation_rate = mutation_rate
        self.timing_cap = timing_cap
        self.fitness = 0
        
    def mutate(self):
        # For each intersection check if there is a mutation        
        rng = default_rng()
        for i, schedule in enumerate(self.schedules.values()):
            mutation_chance = rng.random()
            # If a mutation takes place, replace one timing in the schedule 
            # with a random number under the cap
            if mutation_chance <= self.mutation_rate:
                random_index = rng.integers(0, len(schedule))
                random_timing = rng.integers(1, self.timing_cap, endpoint=True)
                schedule[random_index] = random_timing
                self.schedules[i] = schedule
                
    def update_fitness(self, score):
        self.fitness = score
        
    def copy(self, fitness = False):
        ind = Individual(self.schedules, mutation_rate = self.mutation_rate, timing_cap = self.timing_cap)
        if fitness == True:
            ind.update_fitness(self.fitness)
        return ind
                
class Population:
    
    def __init__(self, sim, intersection_dict, gen_size=2, candidate_size=2, timing_cap = 10, mutation_rate = 0.001):
        """
        Class containing a Simulation object and a set of Individual objects
        needed to run an EA to optimize.

        Parameters
        ----------
        sim : Simulation
            Simulation object that defines the shape of any Individuals and 
            allows for their evaluation.
        intersection_dict : dict 
            dictionary defining an undirected graph representation of the 
            simulated traffic situation.
        gen_size : integer, optional
            Defines size of each generation, must be 2 or larger. The default is 2.
        candidate_size : int, optional
            How much offspring is generated for each generation, must be 2 or larger. 
            The default is 2.
        timing_cap : integer, optional
            Defines the maximum amount of iterations a certain light is allowed 
            to stay green before cycling. The default is 10.
        mutation_rate : float, optional
            Chance for the schedule of every intersection to mutate. The default is 0.001.


        """
        
        self.sim = sim
        self.intersection_dict = intersection_dict
        
        self.timing_cap = timing_cap
        self.mutation_rate = mutation_rate
        self.gen_size = gen_size
        self.candidate_size = candidate_size
        
        # Initialize list to hold Individual objects
        self.individuals = []
        
        # Generate intial random pop
        for i in range(self.gen_size):
            self.random_individual()
            
        for individual in self.individuals:
            self.evaluate_ind(individual)
        
    def random_individual(self):
        # Generate a random schedule and store as Individual
        schedules = defaultdict(list)
        rng = default_rng()
        
        for int_id, intersection in self.sim.intersections.items():
            schedules[int_id].extend(rng.integers(0, self.timing_cap, len(intersection.schedule)))
        
        self.individuals.append(Individual(schedules, mutation_rate = self.mutation_rate, timing_cap = self.timing_cap))
    
    def load_ind_into_sim(self, individual):
        # Reset Simulation object and set schedule to match Individual
        self.sim.reset()
        for int_id in self.sim.intersections.keys():
            for i, street in enumerate(self.sim.intersections[int_id].schedule.keys()):
                self.sim.intersections[int_id].set_schedule(street, individual.schedules[int_id][i])
    
    def evaluate_ind(self, individual):
        # Load schedule from Individual into simulation and perform a full run to
        # get a score.
        self.load_ind_into_sim(individual)
        score = self.sim.full_run()
        individual.update_fitness(score)
        
    def reproduce(self, ind_1, ind_2):
        # Use two members of current generation to generate two offspring
        
        rng = default_rng()
        # Randomly determine crossover ratio
        cross_ratio = rng.random()
        # Randomly determine seed point for spatial crossover set
        cross_seed = rng.integers(0, len(self.sim.intersections))
        
        # Find connected nodes to form a set for crossover
        cross_set = self.find_connected_set(cross_seed, int(cross_ratio*len(self.sim.intersections)))
        
        # Initialize children by copying parents.
        child_1 = ind_1.copy()
        child_2 = ind_2.copy()
        
        # Perform crossover
        for int_id in cross_set:
            child_1.schedules[int_id] = ind_2.schedules[int_id]
            child_2.schedules[int_id] = ind_1.schedules[int_id]
            
        # Check for mutation
        child_1.mutate()
        child_2.mutate()
        
        # Evaluate children
        self.evaluate_ind(child_1)
        self.evaluate_ind(child_2)
        
        return [child_1, child_2]
    
    def next_generation(self):
        nr_of_reproductions = int(self.candidate_size/2)
        
        # Initialize candidates for next generation by copying current generation.
        candidates = [] + self.individuals
        
        # Generate additional candidates through reproduction
        for i in range(nr_of_reproductions):
            # self.select_parents TODO
            parent_1, parent_2 = np.random.choice(self.individuals, 2, False)
            candidates = candidates + self.reproduce(parent_1, parent_2)
        
        # Pick gen_size best performing candidates as next generation
        candidates = np.array(candidates)
        fitness_per_candidate = np.array([c.fitness for c in candidates])
        indices = (-fitness_per_candidate).argsort()[:self.gen_size]
        self.individuals = list(candidates[indices])
        
        # Return fitness metrics of current generation
        fitness_per_ind = np.array([i.fitness for i in self.individuals])
        return fitness_per_ind.max(), fitness_per_ind.min(), fitness_per_ind.mean()
        
    def find_connected_set(self, seed_point, set_size):
        # Use random seed point to generate a set of spatially close nodes
        # through a BFS search
        
        # Initialize connected set by incorporating seed point
        visited = [seed_point]
        
        # Initialize search queue by appending all connected nodes from seed point
        to_visit = deque(self.intersection_dict[seed_point])
        
        # Perform BFS until visited set size equals the required size
        while len(visited) < set_size:
            next_node = to_visit.popleft()
            to_visit.extend(self.intersection_dict[next_node])
            visited.append(next_node)
        
        return visited
    
    def run(self, nr_gens, verbose = True):
        # Perform a run of nr_gens subsequent generations, storing the intermediate
        # metrics.
        best_run = []
        worst_run = []
        mean_run = []
        
        actual_changes = 0
        
        if verbose:
            for i in trange(nr_gens):
                best, worst, mean = self.next_generation()
                best_run.append(best)
                worst_run.append(worst)
                mean_run.append(mean)

                if len(best_run) > 3:
                    if not np.equal(best_run[-2], best):
                        actual_changes+=1
                        success_rate = actual_changes / i
                        print(f"Generation {i} - best: {best}, worst: {worst}, mean: {mean}, success rate: {success_rate:.2f}")
        else:
            for i in range(nr_gens):
                best, worst, mean = self.next_generation()
                best_run.append(best)
                worst_run.append(worst)
                mean_run.append(mean)
            
        return best_run, worst_run, mean_run
        
        