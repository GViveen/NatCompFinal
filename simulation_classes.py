# -*- coding: utf-8 -*-
"""
Created on Mon May  3 09:08:40 2021

@author: Glenn
"""

from collections import defaultdict, deque
import random
from tqdm import trange

class Intersection:
    
    def __init__(self):
        """
        Class to hold information about a single intersection.
        Stores incoming streets and the cars waiting for a green on those streets
        Also contains the schedule for the intersection and its current state within a cycle
        """
        # Initialize schedule as dict with street names as keys and ints as values
        self.schedule = defaultdict(int)
        # Initialize queues as dict of queues with street names as keys
        self.queues = defaultdict(deque)
        # Initialize counter for schedule cycling
        self.counter = 0 
        
    def add_incoming(self, street_name, sched_time=1):
        # Add an incoming street to the intersection
        self.schedule[street_name] = sched_time
        self.cycle = self.sched_to_cycle()
        self.queues[street_name] = deque()
        
    def set_schedule(self, street_name, sched_time):
        # Change the timing for a certain street
        self.schedule[street_name] = sched_time
        self.cycle = self.sched_to_cycle()
        
    def add_to_queue(self, street_name, car):
        # Add a car into the queue from a certain street
        self.queues[street_name].append(car)
        
    def sched_to_cycle(self):
        # Reset cycle to match most recent schedule
        return deque(self.schedule.items())
    
    def reset(self):
        # Reset entire intersection, clearing all queues and setting counter to 0
        self.counter = 0
        self.cycle = self.sched_to_cycle()
        for street in self.queues:
            self.queues[street] = deque([])

        
class Car:
    
    def __init__(self, path):
        """
        Class to hold important information on a single vehicle.
        Stores the distance to the next intersection, as well as the route.

        Parameters
        ----------
        path : list
            path contains an *ordered* list of street 
            identifiers which the car wants to visit.
        """
        self.path = deque(path)
        
        self.current_street = self.path[0]
        self.path.popleft()
        self.distance_to_next = 0


class Simulation:
    
    def __init__(self, streets, paths, score_per_car, nr_iters):
        """
        Class used to efficiently run simulations.
        Stores a list of Car and Intersection objects, as well as a dict
        of streets, their identifiers and the intersections at which they end.
        
        Also stores simulation parameters: number of iterations in a full run,
        scores gained per car.

        Parameters
        ----------
        streets : dict
            dictionary of streets using their identifiers as keys and a tuple
            containing the intersection identifier where they end, and their length.
        paths : list
            list of lists, containing all the paths all the cars should take.
        score_per_car : int
            integer setting the score gained per car that completes its route.
        nr_iters : int
            integer setting the number of iterations for a single simulation.

        """
        # Set parameters and store those necessary for resetting.
        self.streets = streets
        self.intersections = defaultdict(Intersection)
        self.cars = defaultdict(Car)
        self.score = 0
        self.score_per_car = score_per_car
        self.current_iter = 0
        self.nr_iters = nr_iters
        self.original_paths = paths
        
        # Build dict of Intersection objects using street dict
        for k, v in self.streets.items():
            self.intersections[v[0]].add_incoming(k)
        
        # Build dict of Car objects using paths
        for i, path in enumerate(paths):
            car = Car(path)
            self.cars[i] = car
            # Cars start waiting at the end of their first street, so queue them up.
            self.get_in_queue(i)
    
    def iterate_intersection(self, int_id):
        # Check if light changes
        if self.intersections[int_id].counter >= self.intersections[int_id].cycle[0][1]:
            self.intersections[int_id].cycle.rotate(-1)
            self.intersections[int_id].counter = 0
        
        # Let through any waiting car
        if len(self.intersections[int_id].queues[self.intersections[int_id].cycle[0][0]]) > 0:
            self.pass_green(self.intersections[int_id].queues[self.intersections[int_id].cycle[0][0]][0])
            self.intersections[int_id].queues[self.intersections[int_id].cycle[0][0]].popleft()
        
        # Increment counter
        self.intersections[int_id].counter += 1
        
    def iterate_car(self, car_id):
        # If a car still needs to travel before hitting a light, do so.
        if self.cars[car_id].distance_to_next > 0:
            self.cars[car_id].distance_to_next -= 1
            # If a car reaches distance 0, it has to queue up for the light.
            if self.cars[car_id].distance_to_next == 0:
                self.get_in_queue(car_id)
                
    def get_in_queue(self, car_id):
        # Put a Car in the correct queue of the correct Intersection
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
            self.score += self.nr_iters - self.current_iter
            self.cars.pop(car_id)
            
    def iterate(self):
        # Call the iterate function for the intersections first, to let through any cars that are queued
        # Afterwards, iterate all cars that are not still in queue. Then increment current iteration counter.
        for int_id in self.intersections.keys():
            self.iterate_intersection(int_id)
        for car_id in self.cars.keys():
            self.iterate_car(car_id)
        self.current_iter += 1
            
    def full_run(self, verbose=False):
        # Do a full run of the simulation.
        if verbose == True:
            for i in trange(0, self.nr_iters):
                self.iterate()
        else: 
            for i in range(0, self.nr_iters):
                self.iterate()
        return self.score
        
    def reset(self):
        # Reset the simulation to its initial state.
        for intersection in self.intersections.values():
            intersection.reset()
            
        for i, path in enumerate(self.original_paths):
            car = Car(path)
            self.cars[i] = car
            self.get_in_queue(i)
        
        self.score = 0
        self.current_iter = 0
        
class Grid:
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    
    class Intersection:
        def __init__(self, id):
            self.id = id
            
    class Street:
        def __init__(self, start, end, length):
            self.start = start
            self.end = end
            self.name = Grid.gen_street_name(start, end)
            self.length = length
            
        def __repr__(self):
            return f"{self.start} {self.end} {self.name} {self.length} \n"
                
    def __init__(self, width):
        self.grid = list()
        self.width = width
        self.streets = dict()
        count = 0
        for r in range(width):
            l = list()
            for c in range(width):
                l.append(Grid.Intersection(r*width+c))
                count +=1
            self.grid.append(l)
        self.num_intersections = count
            
    def neighbors(self, row, col):
        """Returns neighboring intersections of intersection at specified location

        Args:
            row (int): row
            col (int): column

        Returns:
            4-tuple of Grid.Intersection: neighbors
        """
        width = self.width
        r = row
        c = col
        top = self.grid[r-1][c] 
        bottom = self.grid[(r+1)%width][c]
        left = self.grid[r][c-1]
        right = self.grid[r][(c+1)%width]
        return (top,bottom,left,right)
    
    def gen_street_name(start, end) -> str:
        """Generates a street name based on the intersection on the start and end of the street

        Args:
            start (int): ID of intersection at start of street
            end (int): ID of intersection at the end of the street

        Returns:
            str: Street name
        """
        start = [int(char) for char in str(start)]
        end = [int(char) for char in str(end)]
        string = ""
        for i in start:
            string += f"{Grid.alphabet[i]}"
        string += "-"
        for j in end:
            string += f"{Grid.alphabet[j]}"
        return string
            
    def gen_grid_description(self) -> str:
        """Returns description of the grid in hashcode input format

        Returns:
            str: description of grid
        """
        width = self.width
        data = ''
        for r in range(width):
            row = self.grid[r]
            for c in range(len(row)): # for each intersection
                intersection = self.grid[r][c] # get the intersection
                # get the connected intersections in all 4 directions
                streets = self.neighbors(r, c)
                for s in streets:
                    street = Grid.Street(intersection.id, s.id, 40)
                    self.streets[street.name] = street
                    data+= repr(street)
                    
        return data
    
    def gen_grid_cars(self, amount, operations) -> str:
        """ Returns generated cars in hashcode input format
        
        Args:
            amount (int): Number of cars to generate
            operations (int): Number of operations a car is given
            
        Returns:
            str: Description of cars and their routes
        """
        width = self.width
        data = ''
        for c in range(amount):
            data += f"{operations} "
            row = random.randint(0, width-1)
            col = random.randint(0, width-1) 
            current = self.grid[row][col]
            prev = None
            for i in range(operations):
                neighbours = list(self.neighbors(current.id // width, current.id%width))
                if prev != None:
                    neighbours.remove(prev)
                rand_next = neighbours[random.randint(0, len(neighbours)-1)]
                street_name = Grid.gen_street_name(current.id, rand_next.id)
                if street_name in self.streets:    
                    data += street_name + ' '
                    prev = current
                    current = rand_next
                else:
                    raise("Invalid street name")
                
            data += '\n'
        return data
                
                
    
    def gen_hashcode_string(self, duration, num_cars, hops, bonus_points = 1000, save = False, name='') -> str:
        """Generates hashcode data string

        Args:
            duration (int): duration of the simulation.
            num_cars (int): number of cars.
            hops (int): number of hops.
            bonus_points (int, optional): Bonus points we get when car finishes within duration.
            save (bool, optional): Whether to save the file to de ./data folder. Defaults to False.
            name (str, optional): Name of the file when saved. Defaults to ''.

        Returns:
            str: Data in string format
        """
        data = ""
        data += self.gen_grid_description()
        data += self.gen_grid_cars(num_cars, hops)
        
        # prepend info
        data = f"{duration} {self.num_intersections} {len(self.streets)} {num_cars} {bonus_points} \n" + data

        if save and name:
            file = open(f'./data/{name}', "w+")
            file.write(data)
            file.close()
        
        return data