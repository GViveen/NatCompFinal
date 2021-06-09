# NatCompFinal
This repository contains our implementation for the final project of the Natural Computing course, with the title: Optimization of Traffic Signaling.

Authors: Clara Rus, Marco Post, Glenn Viveen

### Project Description
For this project we got inspired by the Hash Code 2021 - Traffic Signaling challengeKaggle challenge. In order to solve the problem described by this challenge, we plan to use an Evolu-tionary Algorithm to optimize the schedule of traffic lights in a city plan designed by us, but inspired from the one presented by the Kaggle challenge. We believe that thisis the most suited approach for this task, as it is essentially a numeric optimizationproblem of the schedule of each traffic light. 

### Data for Simulation
You can find the generated city plans in the data folder:
* hashcode.in - city plan offered by kaggle
* test.in simple - square grid 
* complex_test.in - complex city plan 

### Run Simulation
To run the simulation you just need to run the main.py file. 

If you want to generate a new city plan use the `--new_file` argument, otherwise it will run the simulation using the existing one. 
