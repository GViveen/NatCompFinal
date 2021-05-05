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
        self.sim = sim
        self.intersection_dict = intersection_dict
        
        self.timing_cap = timing_cap
        self.mutation_rate = mutation_rate
        self.gen_size = gen_size
        self.candidate_size = candidate_size
        self.individuals = []
        
        # Generate intial random pop
        for i in range(self.gen_size):
            self.random_individual()
            
        for individual in self.individuals:
            self.evaluate_ind(individual)
        
    def random_individual(self):
        schedules = defaultdict(list)
        rng = default_rng()
        
        for int_id, intersection in self.sim.intersections.items():
            schedules[int_id].extend(rng.integers(0, self.timing_cap, len(intersection.schedule)))
        
        self.individuals.append(Individual(schedules, mutation_rate = self.mutation_rate, timing_cap = self.timing_cap))
    
    def load_ind_into_sim(self, individual):
        self.sim.reset()
        for int_id in self.sim.intersections.keys():
            for i, street in enumerate(self.sim.intersections[int_id].schedule.keys()):
                self.sim.intersections[int_id].set_schedule(street, individual.schedules[int_id][i])
    
    def evaluate_ind(self, individual):
        self.load_ind_into_sim(individual)
        score = self.sim.full_run()
        individual.update_fitness(score)
        
    def reproduce(self, ind_1, ind_2):
        rng = default_rng()
        cross_ratio = rng.random()
        cross_seed = rng.integers(0, len(self.sim.intersections))
        
        cross_set = self.find_connected_set(cross_seed, int(cross_ratio*len(self.sim.intersections)))
        
        child_1 = ind_1.copy()
        child_2 = ind_2.copy()
        
        for int_id in cross_set:
            child_1.schedules[int_id] = ind_2.schedules[int_id]
            child_2.schedules[int_id] = ind_1.schedules[int_id]
            
        child_1.mutate()
        child_2.mutate()
        
        self.evaluate_ind(child_1)
        self.evaluate_ind(child_2)
        
        return [child_1, child_2]
    
    def next_generation(self):
        nr_of_reproductions = int(self.candidate_size/2)
        candidates = [] + self.individuals
        for i in range(nr_of_reproductions):
            # self.select_parents TODO
            parent_1 = self.individuals[0]
            parent_2 = self.individuals[1]
            candidates = candidates + self.reproduce(parent_1, parent_2)
        
        candidates = np.array(candidates)
        fitness_per_candidate = np.array([c.fitness for c in candidates])
        indices = (-fitness_per_candidate).argsort()[:self.gen_size]
        self.individuals = list(candidates[indices])
        
        return fitness_per_candidate.max(), fitness_per_candidate.min(), fitness_per_candidate.mean()
        
    def find_connected_set(self, seed_point, set_size):
        visited = [seed_point]
        to_visit = deque(self.intersection_dict[seed_point])
        while len(visited) < set_size:
            next_node = to_visit.popleft()
            to_visit.extend(self.intersection_dict[next_node])
            visited.append(next_node)
        
        return visited
    
    def run(self, nr_gens, verbose = True):
        best_run = []
        worst_run = []
        mean_run = []
        if verbose:
            for i in trange(nr_gens):
                best, worst, mean = self.next_generation()
                best_run.append(best)
                worst_run.append(worst)
                mean_run.append(mean)
            
            return best_run, worst_run, mean_run
        
        else:
            for i in range(nr_gens):
                best, worst, mean = self.next_generation()
                best_run.append(best)
                worst_run.append(worst)
                mean_run.append(mean)
            
            return best_run, worst_run, mean_run
        
        