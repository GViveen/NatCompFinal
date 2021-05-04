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
        
        
class Grid:
    alphabeth = 'abcdefghijklmnopqrstuvwxyz'
    
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
            string += f"{Grid.alphabeth[i]}"
        string += "-"
        for j in end:
            string += f"{Grid.alphabeth[j]}"
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