# Genetic Algorithm script for clustering

# First Run: 6/29/11
# Last Update: 10/20/11

# Description:
#   See Kapetanios Journal of Economic Dynamics & Control 30 (2006) 1389-1408 for theory and background.
#   I've probably over commented this code, but if I don't, I won't remember what I did 6 months from now.

# Author:
#   Taylor Smith
#   University of Mississippi
#   jtsmith2@gmail.com

from numpy import *
import random
import time
import os.path

#Defining global constants
population = 20        #Size of population, i.e., number of genetic strings per generation (MUST BE EVEN)
strlength = 3728      #Length of genetic string (number of units being clustered)
parameters = 13          #Number of variables in X (including constant term)
crossover_rate = 1.00  #Set from 0-1 on how often crossover occurs 
#mutation_rate = 0.1   #Set form 0-1 on how often mutation occurs
mutation_rate = 1-((0.3)**(1.0/(1.0*strlength)))  #From Dorsey code. Bases mutation rate on number of strlength being estimated
reinsert_gen = 15      #determines at which generation the best estimated string so far is reinserted into the population of strings
reinsert_step = 10              #The number of generations between inserting the "best" string so far back into the generation
maxgen = 5000         #Maximum number of generations per loop
#maxgen = strlength*(2000+(strlength-2)*250)  #From Dorsey code
stop_delta = 1.0E-8    #If improvement between loops is less than this, program terminates
loops = 500             #Number of times the optimization will run
max_clusters = 100
min_clusters = 8

#Defining global variables
top_value=0            #Stores the highest value of the objective function found
top_string = []        #Stores the string that generated top_value
top_loop_value = 0     #Stores the highest value of the objective function found in a given loop
top_loop_string = []   #Stores the string that generated top_loop_value
dataX = []
dataY = []
save_location = 'D:\Documents\Working Papers\School Quality on Home Prices\Genetic-Algorithm---Clustering\\'
clusters = 0

#initalizing some values...
generationnum = 0
strnum = 0
top_value_start = 0
reinsert_gen2 = reinsert_gen

# Defining functions to use later
def main_program(): #Main program run by last line of this code.
        global top_value        
        global top_string       
        global top_loop_value     
        global top_loop_string 
        global dataX
        global dataY
        global generationnum
        global reinsert_gen2
        global top_value_start
        global clusters
        
        print "Starting Algorithm"
        print "Max Generations:", maxgen
        print "Mutation Rate:", mutation_rate
        print "Start Time:", time.strftime("%I:%M:%S")
        
        dataX = genfromtxt('StataDataX.csv', delimiter=",")
        dataY = genfromtxt('StataDataY.csv', delimiter=",")
        
        gen = zeros((population, strlength))  #Create a 2-D array of size population by strlength.  This will be the "generation".

        for k in xrange(min_clusters, max_clusters):

                clusters = k
                print "---------------------------------------------------------------------"
                print "Clusters:", k
        
                #This loops the optimization a specified number of times so that we're not relient on the inital random assignment
                for x in xrange(loops):
                        print "---------------------------------------------------"
                        print "Loop:", x
                        top_loop_value = 0
                        top_loop_string = []
                        reinsert_gen2 = reinsert_gen
                        
                        #Randomly assign each element in gen a cluster number  (Can this be done better than randomly?)
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
                                if os.path.isfile(save_location + 'TopString' + str(clusters) + '.npy'): #Loads best string if the file exists (in event of power loss)
                                        gen[0] = load(save_location + 'TopString' + str(clusters) + '.npy')

                        top_value_start = top_value #Records what the best value was at the start of the loop.

                        genruntime = zeros(500) #Stores last 500 runtimes
                        
                        #The genetic algorithm
                        for gener in xrange(maxgen):
                                t0 = time.clock() #Record start time for this iteration
                                generationnum = gener
                                if gener % 500 == 0:  #Gives some summary stats every so often, also saves best string in case of power loss, etc
                                        print "Generation:", gener, "| Time:", time.strftime("%I:%M:%S"), "| Top Value:", top_value, "| Avg Runtime:", genruntime.mean()
                                        with open(save_location + 'Output' + str(clusters) + '.txt', 'a') as f:
                                                        f.write("Generation: " + str(gener) + " | Time: " + time.strftime("%I:%M:%S") + " | Top Value: " + str(top_value) + " | Avg Runtime: " + str(genruntime.mean()) + "\n")
                                        if gener % 500 == 0: #could be set to happen less frequently if the above output happens very frequently.
                                                savetxt(save_location + 'TopString' + str(clusters) + '.txt', top_string) #For easy input into excel
                                                save(save_location + 'TopString' + str(clusters) + '.npy', top_string) #Easy to read back into program
                       
                                prob = calc_fitness(gen) #generates an array of probabilies based on fitness level
         
                                newgen = draw_from_current(gen, prob) #draws new group from old using above calculated probabilities
         
                                newgen = crossover(newgen, gener) #crossover step where strings are paired and combined to form new strings

                                gen = mutate(newgen, gener) #mutate step to randomly assign some bits to new clusters, and if reinsert_gen, does that

                                genruntime[gener % 500] = time.clock() - t0  #Saves runtime of gen to array

                                
                        print "Best value of objective function after cycle:", top_loop_value
                        
                        #Stop condition
                        if abs(top_value_start - top_value) < stop_delta and x > 1:  #If there's been no (or little) improvement in the loop, stop.
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
                        
        
        fitness = fitness - fitness.min()
        if fitness.sum() == 0:
                fitsum = 1
                print "All zero fitness"
        else:
                fitsum = fitness.sum()
                
        result = fitness / float(fitsum)  #Normalize the fitness values to probabilities that sum to 1
        return result
        
def draw_from_current(generation, probability): #draws the pool for the new generation with replacement based on probabilities generated in calc_fitness above
        warray = zeros((1000, strlength))
        probability = probability*1000
        
        #Creates a new array based on the probabilities figured.  For example, say there are 4 strings: A,B,C,D with probabilities .5, .2, .2, .1 respectivily.
        #We generate an array of the form [A,A,A,A,A,B,B,C,C,D] and then randomly generate an index 0-9 and assign the string at that index to the result.
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
                        #Example:
                        #   Gen[0] = [1,2,3,4,5]
                        #   Gen[1] = [6,7,8,9,0]
                        #   cut_index = 3
                        #   *perform crossover*
                        #   Gen[0] = [1,2,3,9,0]
                        #   Gen[1] = [6,7,8,4,5]
                
        return generation
        
def mutate(generation, gennum): #Randomly mutates individual string bits based on a set probability
        global reinsert_gen
        global reinsert_gen2
        
        for i in xrange(population):
                for j in xrange(strlength):
                        if random.random() < mutation_rate:
                                generation[i,j] = random.randrange(clusters)
        
        if gennum == reinsert_gen2:  #reseeds the best string so far back into the population
                generation[random.randrange(population)] = top_string
                reinsert_gen2 += reinsert_step
                
        return generation
        
def objfunc(str): #Returns the value of the objective function for the given string
        #Creates empty 2-D arrays for each cluster of the correct size (X and Y), and appends them to a list
        clusterdataX = list([])
        clusterdataY = list([])

        #Sorts data by cluster
        for x in xrange(clusters):
                indicies = where(str==x)  #list of indicies for cluster X
                try:
                        clusterdataX.append(dataX[indicies])  #Uses advanced slicing to return data from X and Y only at indicies
                        clusterdataY.append(dataY[indicies])
                except:
                        print "Element:", indicies
                        set_printoptions(threshold=5000)
                        print "String:", str
                        raise

        #Performs the OLS regression on each cluster, and stores the SSR
        ssr = zeros((clusters))
        for i in xrange(clusters):
                if clusterdataX[i].shape[0] > parameters:  #basic check for full rank
                        clusterdataX[i] = varianceCheck(clusterdataX[i])  #gets rid of constant or colinear columns
                        ssr[i] = ols(clusterdataY[i], clusterdataX[i], i)
                else:
                        ssr[i] = 0

        #calculates the AIC based on the SSRs of the above regressions     
        return -log(ssr.sum()/strlength) - 2*clusters*parameters/strlength
        
def varianceCheck(x):
        #Check to see if Age is all 0s and one other number (makes Age and Age^2 columns colinear)
        uni = unique(x[:,1]) #finds unique values in column #2 (Age)
        if uni.shape[0] == 2 and uni.min()==0:  #if there's only 2 unique values and one of them is 0, X.T*X will be singular...
                x = delete(x, 2, 1)  # so we drop Age^2.
        
        #Removes any columns where there is no variation (except for the first column of ones)
        v = x.var(axis=0)  #get variance of each column
        indicies = where(v==0)  #list where variance == 0
        x = delete(x, indicies[0][1:], 1)  #deletes those columns
        
        return x

def ols(y,x,c=0):
        try:
                inv_xx = linalg.inv(dot(x.T,x))
        except linalg.LinAlgError:
                set_printoptions(threshold=5000)
                print "Singular Matrix encountered", x, generationnum, strnum, c
                return 0
        xy = dot(x.T,y)
        b = dot(inv_xx,xy)
        e = y - dot(x,b)
        return dot(e.T,e)
        
        
        
main_program()  #runs the main program

