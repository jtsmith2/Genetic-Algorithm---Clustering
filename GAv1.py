# Genetic Algorithm script for clustering
# 6/29/2011
# Taylor Smith

from numpy import *
import random
import time

#Defining global constants
population = 20        #Size of population to originally start with
parameters = 4000      #Number of parameters we are estimating
crossover_rate = 1.00  #Set from 0-1 on how often crossover occurs 
#mutation_rate = 0.1   #Set form 0-1 on how often mutation occurs
mutation_rate = 1-((0.3)**(1.0/(1.0*parameters)))  #From Dorsey code. Bases mutation rate on number of parameters being estimated
reinsert_gen = 100      #determines at which generation the best estimated string so far is reinserted into the population of strings
reinsert_step = 10		#The number of generations between inserting the "best" string so far back into the generation
maxgen = 5000000         #Maximum number of generations
#maxgen = parameters*(2000+(parameters-2)*250)  #From Dorsey code
stop_delta = 1.0E-8    #If improvement between loops is less than this, program terminates
clusters = 10          #Number of clusters to sort into including "not clustered"
loops = 10             #Number of times the optimization will run

#Defining global variables
top_value=0            #Stores the highest value of the objective function found
top_string = []        #Stores the string that generated top_value
top_loop_value = 0     #Stores the highest value of the objective function found in a given loop
top_loop_string = []   #Stores the string that generated top_loop_value
reinsert_gen2 = reinsert_gen

# Defining functions to use later
def main_program(): #Main program run by last line of this code.
	global top_value        
	global top_string       
	global top_loop_value     
	global top_loop_string  
	
	print "Starting Algorithm"
	print "Max Generations:", maxgen
	print "Mutation Rate:", mutation_rate
	print "Start Time:", time.strftime("%I:%M:%S")
	
	gen = zeros((population, parameters))  #Create a 2-D array of size population by parameters
	
	#This loops the optimization a specified number of times so that we're not relient on the inital random assignment
	for x in xrange(loops):
		print "---------------------------------------------------"
		print "Loop:", x
		top_loop_value = 0
		top_loop_string = []
		reinsert_gen2 = reinsert_gen
		
		#Randomly assign each element in gen a cluster number
		for i in xrange(population):
			for j in xrange(parameters):
				gen[i,j] = random.randrange(clusters)
			
		if x == 0:
			start_value = objfunc(gen[0,:]) #Pass first string to get inital value of objective function
			top_loop_value = start_value  #save the value of the best string so far
			top_loop_string = gen[0,:]  #the best string so far (the only string so far)
			top_value = top_loop_value
			top_string = top_loop_string
			print "Intial value of objective function:", start_value
		
		#The genetic algorithm
		for gener in xrange(maxgen):
			if gener % 1000 == 0:
				print "Generation:", gener, "| Time:", time.strftime("%I:%M:%S"), "| Top Loop Value:", top_loop_value, "| Overall Top Value:", top_value
			#print "Start Gen", gen
			prob = calc_fitness(gen) #generates an array of probabilies based on fitness level
			#print "Probabilities:"
			#print prob
			newgen = draw_from_current(gen, prob) #draws new group from old using above calculated probabilities
			#print "Gen after draw:"
			#print newgen
			newgen = crossover(newgen, gener) #crossover step where strings are paired and combined to form new strings
			#print "Gen after crossover"
			#print newgen
			gen = mutate(newgen, gener) #mutate step to randomly assign some bits to new clusters, and if reinsert_gen, does that
			#print "Gen after mutate"
			#print gen
			
		print "Best value of objective function after cycle:", top_loop_value
		
		#Stop condition
		if abs(top_loop_value - top_value) < stop_delta and x > 1:
			print "Stop condition met."
			break;
		
	print "Program Complete"
	print "Optimal value of objective function", top_value
	print "Optimal string:"
	print top_string
		
	
def calc_fitness(generation): #Calculates fitness values and generates the draw probabilities from those values
	global top_loop_value
	global top_loop_string
	global top_value
	global top_string
	
	fitness = zeros((population))
	
	for x in xrange(population):
		fitness[x] = objfunc(generation[x])  #Calculate objective function for each string
		if fitness[x] > top_loop_value:  #Replace top value and string if necessary
			top_loop_value = fitness[x]
			top_loop_string = generation[x]
			if top_loop_value > top_value:
				top_value = top_loop_value
				top_string = top_loop_string
			
	#print "Fitness"
	#print fitness
	fitness = fitness - fitness.min()
	#print fitness.sum()
	result = fitness / float(fitness.sum())  #Normalize the fitness values to probabilities that sum to 1
	return result
	
def draw_from_current(generation, probability): #draws the pool for the new generation with replacement based on probabilities generated in calc_fitness above
	warray = zeros((1000, parameters))
	probability = probability*1000
	
	#Creates a new array based on the probabilities figured.  For example, say there are 4 strings: A,B,C,D with probabilities .5, .2, .2, .1 respectivily.
	#We generation an array of the form [A,A,A,A,A,B,B,C,C,D] and then randomly generate an index 0-9 and assign the string at that index to the result.
	#Now, the below code does the exact same thing, just with 1000 entries (more precision) instead of 10.
	index = 0
	for w in xrange(probability.shape[0]):
		for x in xrange(int(probability[w])):
			warray[index] = generation[w]
			index += 1
	
	result = zeros((population, parameters))
	for i in xrange(population):
		result[i] = warray[random.randint(0,warray.shape[0]-1)]
		
	return result
	
def crossover(generation, gennum): #Performs the crossover step of the GA based on a set probability
	for x in xrange(0,population,2):
		if random.random() < crossover_rate:
			cut = random.randint(1,parameters-2)
			gen1 = generation.copy()
			generation[x,cut:], generation[x+1,cut:] = gen1[x+1,cut:], gen1[x,cut:]
		
	return generation
	
def mutate(generation, gennum): #Randomly mutates individual parameters based on a set probability
	global reinsert_gen
	global reinsert_gen2
	
	for i in xrange(population):
		for j in xrange(parameters):
			if random.random() < mutation_rate:
				generation[i,j] = random.randrange(clusters)
	
	if gennum == reinsert_gen2:
		generation[random.randrange(population)] = top_string
		reinsert_gen2 += reinsert_step
		
	return generation
	
def objfunc(str): #Returns the value of the objective function for the given string
	return str.sum()
	
main_program()  #runs the main program

