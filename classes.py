# -*- coding: utf-8 -*-
"""
Created on Mon May  3 09:08:40 2021

@author: Glenn
"""

from collections import defaultdict, deque
from tqdm import trange

class Intersection:
    
    def __init__(self):
        # Initialize schedule as dict with street names as keys and ints as values
        self.schedule = defaultdict(int)
        # Initialize queues as dict of queues with street names as keys
        self.queues = defaultdict(deque)
        # Initialize counter for schedule cycling
        self.counter = 0 
        
    def add_incoming(self, street_name, sched_time=1):
        self.schedule[street_name] = sched_time
        self.cycle = self.sched_to_cycle()
        self.queues[street_name] = deque()
        
    def set_schedule(self, street_name, sched_time):
        self.schedule[street_name] = sched_time
        self.cycle = self.sched_to_cycle()
        
    def add_to_queue(self, street_name, car):
        self.queues[street_name].append(car)
        
    def sched_to_cycle(self):
        return deque(self.schedule.items())

        
class Car:
    
    def __init__(self, path):
        self.path = deque(path)
        
        self.current_street = self.path[0]
        self.path.popleft()
        self.distance_to_next = 0


class Simulation:
    
    def __init__(self, streets, paths, score_per_car, nr_iters):
        self.streets = streets
        self.intersections = defaultdict(Intersection)
        self.cars = defaultdict(Car)
        self.score = 0
        self.score_per_car = score_per_car
        self.nr_iters = nr_iters
        
        for k, v in self.streets.items():
            self.intersections[v[0]].add_incoming(k)
        
        for i, path in enumerate(paths):
            car = Car(path)
            self.cars[i] = car
    
    def iterate_intersection(self, int_id):
        # Check if light changes
        if self.intersections[int_id].counter >= self.intersections[int_id].cycle[0][1]:
            self.intersections[int_id].cycle.rotate(-1)
            self.intersections[int_id].counter = 0
        
        # Let through any waiting car
        if len(self.intersections[int_id].queues[self.intersections[int_id].cycle[0][0]]) > 0:
            self.pass_green(self.cars[self.intersections[int_id].queues[self.intersections[int_id].cycle[0][0]][0]])
            self.intersections[int_id].queues[self.intersections[int_id].cycle[0][0]].popleft()
        
        # Increment counter
        self.intersections[int_id].counter += 1
        
    def iterate_car(self, car_id):
        if self.cars[car_id].distance_to_next > 0:
            self.cars[car_id].distance_to_next -= 1
            if self.cars[car_id].distance_to_next == 0:
                self.get_in_queue(car_id)
                
    def get_in_queue(self, car_id):
        street_name = self.cars[car_id].current_street
        int_id = self.streets[street_name][0]
        self.intersections[int_id].add_to_queue(street_name, car_id)
        
    def pass_green(self, car_id):        
        # Update street
        self.cars[car_id].current_street = self.cars[car_id].path[0]
        self.cars[car_id].path.popleft()
        if len(self.cars[car_id].path) > 0:
            # Move car onto next street if it is not its last street
            self.cars[car_id].distance_to_next = self.streets[self.cars[car_id].current_street][0]
        else:
            # If car has reached its last street, treat as finished and update score. Then remove car from simulation.
            self.score += self.score_per_car
            self.cars.pop(car_id)
            
    def iterate(self):
        for int_id in self.intersections.keys():
            self.iterate_intersection(int_id)
        for car_id in self.cars.keys():
            self.iterate_car(car_id)
            
    def full_run(self):
        for i in trange(0, self.nr_iters):
            self.iterate()
        print(self.score)