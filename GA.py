from operator import ge
import pandas as pd
import numpy as np
import random

POPULATION_SIZE = 100

DF = None
TESTS = None
FAULT_MATRIX = None

GATE_KEEPER = {
    "frequency":0,
    "APFD":0
}



class Individual(object):
    # Class representing individual in population

    def __init__(self, order,fault_matrix):
        self.order = order
        self.apfd = self.calculate_apfd(order,fault_matrix)

    

    @classmethod
    def create_random_testcase_order(self):

        global TESTS
        c=[]
        c= TESTS.copy()
        random.shuffle(c)
        return list(c)

    @classmethod
    def use_smallfaultmatrix(self):
        
        global DF
        global FAULT_MATRIX
        global TESTS

        DF=pd.read_csv("smallfaultmatrix.csv", header=None)
        DF.columns =['testcases','fault1','fault2','fault3','fault4','fault5','fault6','fault7','fault8','fault9']
        TESTS=DF['testcases']
        FAULT_MATRIX=DF.iloc[:,1:] #all the rows and all columns excluding 1st one

    @classmethod
    def use_bigfaultmatrix(self):

        global DF
        global FAULT_MATRIX
        global TESTS

        DF=pd.read_csv("bigfaultmatrix.csv", header=None)
        
        DF.columns =['testcases','fault1','fault2','fault3','fault4','fault5','fault6','fault7','fault8','fault9','fault10','fault11','fault12','fault13','fault14','fault15','fault16','fault17','fault18','fault19','fault20','fault21','fault22','fault23','fault24','fault25','fault26','fault27','fault28','fault29','fault30','fault31','fault32','fault33','fault34','fault35','fault36','fault37','fault38']
        TESTS=DF['testcases']
        FAULT_MATRIX=DF.iloc[:,1:] #all the rows and all columns excluding 1st one


    def mate(self, par2):
        global FAULT_MATRIX
        child=[]
        par1 = self.order

        crossoverpoint= np.random.randint(1, len(par1)-1)
        prob = random.random()
        if prob < 0.45:
            child=par1[:crossoverpoint]
            for x in par2:
                if x in child:
                    continue
                else:
                    child.append(x)
        elif prob < 0.9:
            child=par2[:crossoverpoint]
            for y in par1:
                if y in child:
                    continue
                else:
                    child.append(y)
        else:
            child = par1.copy()
            #going for mutation
            
            #swap two neighboring testcases in the list
            child[crossoverpoint],child[crossoverpoint+1]=child[crossoverpoint+1],child[crossoverpoint]

        return Individual(child,FAULT_MATRIX)

    def calculate_apfd(self,test_case_order,fault_matrix):

        selected_test=[]   #final test cases chosen for each fault
        fault_revealed =[] #list which will store test cases that reveal each fault
        for clm in fault_matrix: #iterate through columns fault1, fault2,...faultn of fault matrix

            fault_revealed=list(DF['testcases'].loc[DF[clm]==1].values) #fetch all rows of testcases where fault'n' is revealed
        
            #iterate the testcase order and pick the first test case where fault is revealed
            for index,x in enumerate(test_case_order):
                if x in fault_revealed:
                    selected_test.append(x)
                    break;

        sum_tests=0
        #iterate through the list of test cases chosen that reveal all faults 
        #then check the corresponding index of that item in the test case order
        #sum up these indexes in the loop to be used later in formula
        for j in selected_test:
            for index,y in enumerate(test_case_order,1):
                if j == y:
                    sum_tests= sum_tests+index

        num_of_tests=len(test_case_order)
        num_of_faults=len(fault_matrix.columns)

        #implementing the formula for APFD
        apfd= 1 - (sum_tests/(num_of_tests*num_of_faults)) + (1/(2*num_of_tests))
        return round(apfd,5)


def main():
    global TESTS
    global FAULT_MATRIX
    global GATE_KEEPER

    # current generation
    generation = 1

    found = False
    population = []

    
    Individual.use_bigfaultmatrix()
    Individual.use_smallfaultmatrix()

    # create initial population
    for _ in range(POPULATION_SIZE):
        order = Individual.create_random_testcase_order()
        population.append(Individual(order,FAULT_MATRIX))
    print(len(population))
    while not found:


        # sort the population in increasing order of apfd score
        population = sorted(population, key=lambda x: x.apfd,reverse=True)


        if generation == 1:
            GATE_KEEPER['APFD'] = population[0].apfd

        else:
            if GATE_KEEPER['frequency'] >= 100:
                break
            
            if GATE_KEEPER['APFD'] == population[0].apfd:
                GATE_KEEPER['frequency'] += 1
            else:
                GATE_KEEPER['frequency'] = 0
                GATE_KEEPER['APFD'] = population[0].apfd


        # Otherwise generate new generation
        new_generation = []

        # Perform Elitism
        s = int((10*POPULATION_SIZE)/100)
        new_generation.extend(population[:s])

        # Individuals will mate from 50% of fittest population to produce offspring
        s = int((90*POPULATION_SIZE)/100)
        for _ in range(s):
            parent_1 = random.choice(population[:50])
            parent_2 = random.choice(population[:50])

            child = parent_1.mate(parent_2.order)
            
            new_generation.append(child)

        population = new_generation

        print(f"Generation: {generation} APFD1: {population[0].apfd} APFD-1: {population[-1].apfd}")

        generation += 1


    print(f"Test Case order: {population[0].order} APFD: {population[0].apfd}")


if __name__ == '__main__':
    main()
