# Genetic Algorithm script for clustering
# See Kapetanios Journal of Economic Dynamics & Control 30 (2006) 1389-1408 for theory and background.
# 6/29/2011
# Taylor Smith

from numpy import *
import random
import time
import os.path

#Defining global constants
population = 20        #Size of population to originally start with
strlength = 4000      #Length of genetic string (number of units being clustered)
parameters = 3                  #Number of variables in X (not including constant term)
crossover_rate = 1.00  #Set from 0-1 on how often crossover occurs 
#mutation_rate = 0.1   #Set form 0-1 on how often mutation occurs
mutation_rate = 1-((0.3)**(1.0/(1.0*strlength)))  #From Dorsey code. Bases mutation rate on number of strlength being estimated
reinsert_gen = 15      #determines at which generation the best estimated string so far is reinserted into the population of strings
reinsert_step = 10              #The number of generations between inserting the "best" string so far back into the generation
maxgen = 50000         #Maximum number of generations
#maxgen = strlength*(2000+(strlength-2)*250)  #From Dorsey code
stop_delta = 1.0E-8    #If improvement between loops is less than this, program terminates
clusters = 5          #Number of clusters to sort into 
loops = 100             #Number of times the optimization will run

#Defining global variables
top_value=0            #Stores the highest value of the objective function found
top_string = []        #Stores the string that generated top_value
top_loop_value = 0     #Stores the highest value of the objective function found in a given loop
top_loop_string = []   #Stores the string that generated top_loop_value
reinsert_gen2 = reinsert_gen
dataX = []
dataY = []
save_location = 'D:\Documents\Working Papers\School Quality on Home Prices\Genetic-Algorithm---Clustering\\'

generationnum = 0
strnum = 0

# Defining functions to use later
def main_program(): #Main program run by last line of this code.
        global top_value        
        global top_string       
        global top_loop_value     
        global top_loop_string 
        global dataX
        global dataY
        global generationnum
        
        print "Starting Algorithm"
        print "Max Generations:", maxgen
        print "Mutation Rate:", mutation_rate
        print "Start Time:", time.strftime("%I:%M:%S")
        
        dataX = genfromtxt('randomX2.csv', delimiter=",")
        dataY = genfromtxt('randomY2.csv', delimiter=",")
        
        #print dataX.shape[0]
        #print dataY.shape[0]
        
        gen = zeros((population, strlength))  #Create a 2-D array of size population by strlength
        
        #This loops the optimization a specified number of times so that we're not relient on the inital random assignment
        for x in xrange(loops):
                print "---------------------------------------------------"
                print "Loop:", x
                top_loop_value = 0
                top_loop_string = []
                reinsert_gen2 = reinsert_gen
                
                #Randomly assign each element in gen a cluster number
                for i in xrange(population):
                        for j in xrange(strlength):
                                gen[i,j] = random.randrange(clusters)
                        
                
                start_value = objfunc(gen[0,:]) #Pass first string to get inital value of objective function
                top_loop_value = start_value  #save the value of the best string so far
                top_loop_string = gen[0,:]  #the best string so far (the only string so far)
                print "Intial value of objective function:", start_value

                if x == 0:
                        top_value = top_loop_value
                        top_string = top_loop_string
                        if os.path.isfile(save_location + 'TopString.npy'):
                                gen[0] = load(save_location + 'TopString.npy')
                                
                
                #The genetic algorithm
                for gener in xrange(maxgen):
                        generationnum = gener
                        if gener % 1000 == 0:
                                print "Generation:", gener, "| Time:", time.strftime("%I:%M:%S"), "| Top Loop Value:", top_loop_value, "| Overall Top Value:", top_value
                                with open(save_location + 'Output.txt', 'a') as f:
                                                f.write("Generation: " + str(gener) + " | Time: " + time.strftime("%I:%M:%S") + " | Top Loop Value: " + str(top_loop_value) + " | Overall Top Value: " + str(top_value) + "\n")
                                if gener % 1000 == 0:
                                        savetxt(save_location + 'TopString.txt', top_string)
                                        save(save_location + 'TopString.npy', top_string)
                                        
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
        global strnum
        
        fitness = zeros((population))
        
        for x in xrange(population):
                strnum = x
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
        if fitness.sum() == 0:
                fitsum = 1
                print "All zero fitness"
        else:
                fitsum = fitness.sum()
        #print fitness.sum()
        result = fitness / float(fitsum)  #Normalize the fitness values to probabilities that sum to 1
        return result
        
def draw_from_current(generation, probability): #draws the pool for the new generation with replacement based on probabilities generated in calc_fitness above
        warray = zeros((1000, strlength))
        probability = probability*1000
        
        #Creates a new array based on the probabilities figured.  For example, say there are 4 strings: A,B,C,D with probabilities .5, .2, .2, .1 respectivily.
        #We generation an array of the form [A,A,A,A,A,B,B,C,C,D] and then randomly generate an index 0-9 and assign the string at that index to the result.
        #Now, the below code does the exact same thing, just with 1000 entries (more precision) instead of 10.
        index = 0
        for w in xrange(probability.shape[0]):
                for x in xrange(int(probability[w])):
                        warray[index] = generation[w]
                        index += 1
        
        result = zeros((population, strlength))
        for i in xrange(population):
                result[i] = warray[random.randint(0,warray.shape[0]-1)]
                
        return result
        
def crossover(generation, gennum): #Performs the crossover step of the GA based on a set probability
        for x in xrange(0,population,2):
                if random.random() < crossover_rate:
                        cut = random.randint(1,strlength-2)
                        gen1 = generation.copy()
                        generation[x,cut:], generation[x+1,cut:] = gen1[x+1,cut:], gen1[x,cut:]
                
        return generation
        
def mutate(generation, gennum): #Randomly mutates individual string bits based on a set probability
        global reinsert_gen
        global reinsert_gen2
        
        for i in xrange(population):
                for j in xrange(strlength):
                        if random.random() < mutation_rate:
                                generation[i,j] = random.randrange(clusters)
        
        if gennum == reinsert_gen2:
                generation[random.randrange(population)] = top_string
                reinsert_gen2 += reinsert_step
                
        return generation
        
def objfunc(str): #Returns the value of the objective function for the given string
        #Counts the number of homes in each cluster and stores in "incluster"
        incluster = zeros((clusters))
        for element in str:
                try:
                        incluster[element] += 1
                except:
                        print "Element:", element
                        set_printoptions(threshold=5000)
                        print "String:", str
                        raise
        #print incluster
        
        #Creates empty 2-D arrays for each cluster of the correct size (X and Y)
        clusterdataX = list([])
        clusterdataY = list([])
        
        for x in xrange(clusters):
                clusterdataX.append(zeros((incluster[x], parameters)))
                clusterdataY.append(zeros((incluster[x])))

        #print len(clusterdataX)
        #print clusterdataX[1]
        #Sorts the data into the correct cluster data array
        clusterinsertcount = zeros((clusters))
        for i in xrange(strlength):
                clusterdataX[int(str[i])][clusterinsertcount[int(str[i])]] = dataX[i]
                clusterdataY[int(str[i])][clusterinsertcount[int(str[i])]] = dataY[i]
                clusterinsertcount[int(str[i])] += 1
        
        #print clusterinsertcount, clusterdataX[0].shape[0]
        #Performs the OLS regression on each cluster, and stores the SSR
        ssr = zeros((clusters))
        for i in xrange(clusters):
                if clusterdataX[i].shape[0] > parameters:
                        ssr[i] = ols(clusterdataY[i], clusterdataX[i], i)
                else:
                        ssr[i] = 0
        
        #calculates the AIC based on the SSRs of the above regressions
        return -log(ssr.sum()/strlength) - 2*clusters*parameters/strlength
        
def ols(y,x,c=0):
        #print x
        try:
                inv_xx = linalg.inv(dot(x.T,x))
        except linalg.LinAlgError:
                print "Singular Matrix encountered", dot(x.T,x), generationnum, strnum, c
                return 0
        xy = dot(x.T,y)
        b = dot(inv_xx,xy)
        e = y - dot(x,b)
        return dot(e.T,e)
        
        
        
main_program()  #runs the main program

