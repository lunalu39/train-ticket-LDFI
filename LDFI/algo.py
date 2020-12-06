# -*- coding: utf-8 -*-
"""
This file contains algorithm functinos for LDFI. Including recursive fault space exploration, priority calculation, failure scenarios pruning,
CNF conversion, applying SAT solver and computing minimal solutions.
Created on Sat Nov 21 00:38:07 2020

@author: Qingyi Lu and Xiling Zhang
"""
import pycosat
from bidict import bidict
import random
from itertools import chain
import sys
import copy
from util import get_request_type_traces, inject_and_get_trace

#counter for fault injection times
COUNTER = 0

def covertCNF(user_request, services_dict):
    # This function automatically converts the given set of services extracted from the user request into CNF formula
    print("Start converting CNF ", user_request)
    print("Services dict ", services_dict)
    cnf = []
    for s in user_request:
        cnf.append(services_dict[s])
    print("After converting cnf:", cnf)
    return cnf
    
def SATsolver(cnf, isCNF = True):
    # This function using pycosat to generate all the solutions for the given CNF formula. It returns all possible solutions
    print("SAT is solving.........." , cnf)
    cnf_dup = copy.deepcopy(cnf)
    universe = list(set(x for l in cnf_dup for x in l))
    print("Universal set", universe)
    temp_dict = bidict() #temp dict for input CNF into pycosat solver
    i = 1
    for s in universe:
        temp_dict.update([(s, i)])
        i+=1
    print("Temp dict: ", temp_dict)
    for c in cnf_dup:
        for s, index in zip(c, range(len(c))):
            c[index] = temp_dict[s]

    if isCNF == False:
        allSolutions = list(pycosat.itersolve([cnf_dup], prop_limit=50)) #limited prop for SAT solver
        print("All solutions:", allSolutions)
        res = []
        for s in allSolutions:
            temp = [item for item in s if item > 0]
            res.append(temp)
        res = sorted(res, key=len)
    else:
        allSolutions = list(pycosat.itersolve(cnf_dup, prop_limit=50)) #limited prop for SAT solver
        print("All solutions:", allSolutions)
        res = []
        for s in allSolutions:
            temp = [item for item in s if item > 0]
            res.append(temp)
        res = sorted(res, key=len)
    for c in res:
        # print(c)
        for s, index in zip(c, range(len(c))):
            c[index] = temp_dict[:s]
    print("Output from SATsolver function: ",res)
    return res

#remove the negative vaules, sort by size -> remove from universe -> get the min solutions
def getMinSolutions(solutions, cnf):
    # This function compute a minimal set of solutions from the all possible solutions solved by SAT solver. It applys the greedy algorithm 
    # for solving set cover NP problem.
    minSolutions = []
    universe = set(x for l in cnf for x in l)
    print("Input CNF in getMinSolutions function: " ,cnf)
    unique_values = set(chain(*cnf))
    #greedy algorithm for set cover problem 
    while unique_values:
        for s in solutions:
            covered = unique_values & set(s)
            if covered:
                minSolutions.append(s)
                unique_values -= covered
    
    # alternative greedy algorithm for set cover problem 
    # for s in solutions:
    #     if set(s).issubset(unique_values):
    #         minSolutions.append(s)
    #         unique_values = unique_values.difference(set(s))

    print("Output in getMinSolutions: ", minSolutions)
    return minSolutions

def createServiceDict(services):
    # This function create a 1-1 dict to map each service to its unique ID
    services_dict = bidict()
    i = 1
    for s in services:
        services_dict.update([(s, i)])
        i+=1
    print("Service dict: ", services_dict)
    return services_dict

def main(request_type_class, ifRandom = False):
    # This is the main function to apply the LDFI algorithm with/without priority and pruning for all pre-defined request types
    
    ########for testing#######
    # services = ['api', 'reating', 'review', 'replay', 'test']
    # services = ['ts-food-service', 'ts-notification-service', 'ts-seat-service', 'ts-price-service', 'ts-basic-service', 'ts-station-service', 'ts-route-service', 'ts-config-service', 'ts-order-service', 'ts-order-other-service', 'ts-train-service', 'ts-contacts-service', 'ts-consign-price-service', 'ts-user-service', 'ts-travel-service', 'ts-assurance-service', 'ts-security-service', 'ts-preserve-service', 'ts-consign-service', 'ts-ticketinfo-service']
    # fault_type = ['abort', 'delay']

    # preprocess to create dict for all services (sign a ID to each of services)
    services = [ 'ts-user-service', 'ts-auth-service', 'ts-inside-payment-service', 'ts-preserve-other-service', 'ts-rebook-service', 'ts-route-service', 'ts-ticketinfo-service', 'ts-admin-travel-service', 'ts-food-map-service', 'ts-train-service', 'ts-admin-user-service', 'ts-cancel-service', 'ts-ticket-office-service', 'ts-station-service', 'ts-travel-service', 'ts-execute-service', 'ts-preserve-service', 'ts-payment-service', 'ts-contacts-service', 'ts-basic-service', 
    'ts-seat-service', 'ts-admin-route-service', 'ts-admin-basic-info-service', 'ts-travel2-service', 'ts-travel-plan-service', 'ts-consign-price-service', 'ts-security-service', 'ts-verification-code-service', 'ts-route-plan-service', 'ts-price-service', 'ts-order-service', 'ts-assurance-service', 'ts-news-service', 'ts-notification-service', 'ts-config-service', 'ts-food-service', 'ts-consign-service', 'ts-voucher-service', 'ts-admin-order-service', 'ts-order-other-service', 'ts-ui-dashboard', ]
    services = [ch+'.default' for ch in services]
    services_dict = createServiceDict(services)
    # temp = 'ts-food-service'
    # print("test bidict: ", services_dict[temp])
    # temp=1
    # print("test bidict: ",services_dict[:temp])
    
    ########for testing#######
    # pass in a file from tracing that recorded all the call graphs (set of services with order -> dependency) ??
    # request_type_class = [['api', 'reating', 'review', 'replay'],['reating', 'review', 'replay', 'api'],['api', 'reating', 'review', 'test']] #request sets for all request types
    
    # request_type_class = {"login" : ['api', 'reating', 'review', 'replay'],
    #                     "login2" : ['reating', 'review', 'replay', 'api'],
    #                     "login3" : ['api', 'reating', 'review', 'test']}
    # print("request_type_class", request_type_class)
    
    # request1 = ['api', 'reating', 'review', 'replay']
    # request2 = ['reating', 'review', 'replay', 'api']
    # print("test request_type_class: ",request_type_class["login"])
    # print(sorted(request1))
    # print(sorted(request2))
    # print("test request_type_class: ",sorted(request2) == sorted(request1))
    # print("test request_type_class: ",request2 in request_type_class.values())

    # request_type_class = {"login" : ['api', 'reating']}
    # request_type_class = {"login" : ['api', 'reating', 'review', 'replay']}

    # request_type_class = {"preserve" : ['ts-food-service', 'ts-notification-service', 'ts-seat-service', 'ts-price-service', 'ts-basic-service', 'ts-station-service', 'ts-route-service', 'ts-config-service', 'ts-order-service', 'ts-order-other-service', 'ts-train-service', 'ts-contacts-service', 'ts-consign-price-service', 'ts-user-service', 'ts-travel-service', 'ts-assurance-service', 'ts-security-service', 'ts-preserve-service', 'ts-consign-service', 'ts-ticketinfo-service']}
    # request_type_class = {"preserve" : ['ts-food-service', 'ts-notification-service', 'ts-seat-service', 'ts-price-service']}

    # Native LDFI
    if ifRandom:
        request_type_class = get_request_type_traces()
        

        # equvient request class set that grouped by the services
        request_class = []

        all_request_types = request_type_class.keys()

        request_type_tested_FS = dict((el,[]) for el in all_request_types) #store all the tested FS for each request type
        # print("request_type_tested_FS: ", request_type_tested_FS)

        error_FS = dict((el,[]) for el in all_request_types) #store the FS that detected bugs for each request type

        services_total_FS_dict = dict((el,0) for el in services) #store all the tested FS for each service (for computing priority)
        # print("services_total_FS_dict: ", services_total_FS_dict)

        services_error_FS_dict = dict((el,0) for el in services) #store the FS that detected bugs for each service (for computing priority)

        services_pq = dict((el,0) for el in services) #priority for each service

        # main loop to do the recursive fault injections
        for request_type, request in request_type_class.items():
            injection_sce = []
            print("Request type: ",request_type, ", Request: ", request)
            if sorted(request) in request_class:
                continue
            else:
                request_class.append(sorted(request))
            
            print("Request class: ", request_class) 

            clause = covertCNF(request, services_dict)
            prev_cnf = []
            prev_cnf.append(clause)
            # print("prev_cnf: ", prev_cnf)

            to_test_FS = []
            error_IP_prune = []  

            #get min solutions from solver --> injection points --> then combine with fault
            allSolutions = SATsolver(prev_cnf)
            minSolutinos = getMinSolutions(allSolutions, prev_cnf)
            for s in minSolutinos:
                for ft in fault_type:  ## check fault type for services
                    fault_sce = [s, ft]
                    to_test_FS.append([s, ft])

            recursive_solve(prev_cnf, fault_type, to_test_FS, request_type_tested_FS, error_FS, services_pq, services_dict, request_type, services_total_FS_dict, services_error_FS_dict, error_IP_prune, ifSort=False, ifPrune=True)

    else: #LDFI with/without pruning and priority

        # pre-defined subsets
        subset1 = ['type_admin_get_orders', 'type_simple_search', 'type_admin_get_route']
        subset2 = ['type_admin_get_travel', 'type_admin_login',
            'type_cheapest_search', 'type_food_service', 'type_preserve',
            'type_user_login']
        
        #get the services that extracted from traces
        request_type_class = get_request_type_traces()
        request_type_class_subset1 = get_request_type_traces(subset1)
        request_type_class_subset2 = get_request_type_traces(subset2)

        request_class = [] 

        all_request_types = request_type_class.keys()

        request_type_tested_FS = dict((el,[]) for el in all_request_types) #store all the tested FS for each request type
        # print("request_type_tested_FS: ", request_type_tested_FS)

        error_FS = dict((el,[]) for el in all_request_types) #store the FS that detected bugs for each request type

        services_total_FS_dict = dict((el,0) for el in services) #store all the tested FS for each service (for computing priority)
        # print("services_total_FS_dict: ", services_total_FS_dict)

        services_error_FS_dict = dict((el,0) for el in services) #store the FS that detected bugs for each service (for computing priority)

        services_pq = dict((el,0) for el in services) #priority for each service

        # main loop to do the recursive fault injections for subset 1
        for request_type, request in request_type_class_subset1.items():
            injection_sce = []
            print("Request type: ",request_type, ", Request: ", request)
            if sorted(request) in request_class:
                continue
            else:
                request_class.append(sorted(request))
                # print(request_class)
            
            print("Request class: ", request_class) 
            
            clause = covertCNF(request, services_dict)
            prev_cnf = []
            prev_cnf.append(clause)
            # print("prev_cnf: ", prev_cnf)

            to_test_FS = []
            error_IP_prune = []  

            #get min solutions from solver --> injection points --> then combine with fault
            allSolutions = SATsolver(prev_cnf)
            minSolutinos = getMinSolutions(allSolutions, prev_cnf)
            for s in minSolutinos:
                for ft in fault_type:  ## check fault type for services
                    fault_sce = [s, ft]
                    to_test_FS.append([s, ft])

            recursive_solve(prev_cnf, fault_type, to_test_FS, request_type_tested_FS, error_FS, services_pq, services_dict, request_type, services_total_FS_dict, services_error_FS_dict, error_IP_prune)
            
        # main loop to do the recursive fault injections for subset 2
        for request_type, request in request_type_class_subset2.items():
            injection_sce = []
            print("Request type: ",request_type, ", Request: ", request)
            if sorted(request) in request_class:
                continue
            else:
                request_class.append(sorted(request))
            
            print("Request class: ", request_class) 

            clause = covertCNF(request, services_dict)
            prev_cnf = []
            prev_cnf.append(clause)
            # print("prev_cnf: ", prev_cnf)

            to_test_FS = []
            error_IP_prune = [] 

            #get min solutions from solver --> injection points --> then combine with fault
            allSolutions = SATsolver(prev_cnf)
            minSolutinos = getMinSolutions(allSolutions, prev_cnf)
            for s in minSolutinos:
                for ft in fault_type:  ## check fault type for services
                    fault_sce = [s, ft]
                    to_test_FS.append([s, ft])

            recursive_solve(prev_cnf, fault_type, to_test_FS, request_type_tested_FS, error_FS, services_pq, services_dict, request_type, services_total_FS_dict, services_error_FS_dict, error_IP_prune, ifSort=True)

    global COUNTER 
    print("**************************************************************************************************")
    print("Counter for fault injection: ", COUNTER)

def sortByPriority (services_pq, to_test_FS, services_dict):
    # This function sorts the given failure scenarios by the priority for each service
    print("Given failure scenarios in sortByPriority function: ", to_test_FS)
    for i in range(len(to_test_FS)):
        fs = to_test_FS[i]
        value = 0
        # print(fs)
        for s in fs[0]:
            # print(s)
            # print(s, " ", services_pq[services_dict[:s]])
            value = value + services_pq[services_dict[:s]]
        value /= len(fs[0])
        to_test_FS[i].append(value)
    to_test_FS.sort(key = lambda x: -x[2]) 
    for i in range(len(to_test_FS)):
        to_test_FS[i].pop()
    print("Sorted failure scenarios in sortByPriority function: ", to_test_FS)
    return to_test_FS

def randomPriority(services_pq):
    # This function randomly add small priority to the priority of services
    print("Services priority before adding random value", services_pq)
    for k, v in services_pq.items():
        if v == 0:
            services_pq[k] = random.random()
    print("Services priority after adding random value", services_pq)
    return services_pq


def recursive_solve(prev_cnf, fault_type, to_test_FS, request_type_tested_FS, error_FS, services_pq, services_dict, request_type, 
services_total_FS_dict, services_error_FS_dict, error_IP_prune, ifSort = False, ifPrune=True):
    # This function recursively applys the fault injection, with/without pruning and priority
    global COUNTER 
    COUNTER += 1
    if ifSort:
        services_pq = randomPriority(services_pq) #add random priority value to the not reached services
        to_test_FS = sortByPriority(services_pq, to_test_FS, services_dict)
    
    for rand_curr_FS in to_test_FS: 
        print('-------------------------------------------------------')
        print("Testing FSs in recursive_solve function: ", to_test_FS)
        print("Current FS: ", rand_curr_FS)
        
        #check duplicate
        if rand_curr_FS in request_type_tested_FS[request_type]: #check if this FS is already tested for this request type
            continue
        if rand_curr_FS in error_FS[request_type]: #check if this FS is already tested for this request type and find a bug
            continue
        
        #pruning 
        if ifPrune:
            pruning = []
            ifPrune = False
            for fs in error_FS[request_type]:
                pruning.append(fs)
            print("pruning: ", pruning)

            for fs in pruning:
                if fs[1] == rand_curr_FS[1]: #check if fault type is same
                    #check if the current ip is compplicated than one of the error fs
                    if set(fs[0]).issubset(set(rand_curr_FS[0])): 
                        ifPrune = True
            
            if ifPrune:
                print("it pruned!! ")
                continue
        else:
            continue

        inject_points = []
        for i in rand_curr_FS[0]:
            # print("injection point ID: ",i)
            service_name = services_dict[:i]
            # print("injection point service_name: ", service_name)
            inject_points.append(service_name)
            services_total_FS_dict[service_name] += 1  #update pq
        print("Udpate total FS: ", services_total_FS_dict)
        # print("udpate error: ", services_error_FS_dict)
        
        new_call_graph = inject_and_get_trace(inject_points, rand_curr_FS[1], request_type)
        print("New call graph: ", new_call_graph)

        request_type_tested_FS[request_type].append(rand_curr_FS)

        if not new_call_graph:  #find a service error --> detect a bug
            print("New call graph is null, find bug here!")
            error_FS[request_type].append(rand_curr_FS)
            error_IP_prune.append(rand_curr_FS[0])
            for s in inject_points:
                services_error_FS_dict[s] += 1
                services_pq[s] = services_error_FS_dict[s] / services_total_FS_dict[s]  #update priority for each services
            print("Udpate error: ", services_error_FS_dict)
            print("Udpate total: ", services_total_FS_dict)
            print("Updated service priority (find bug): ", services_pq)
        else:
            #for good outcome, update priority
            for s in inject_points:
                services_pq[s] = services_error_FS_dict[s] / services_total_FS_dict[s]  #update priority for each services
            print("Udpate error: ", services_error_FS_dict)
            print("Udpate total: ", services_total_FS_dict)
            print("Updated service priority (new call graph): ", services_pq)

            new_clause = covertCNF(new_call_graph, services_dict)
            print("New clause: ", new_clause)
            prev_cnf.append(new_clause)
            print("New cnf: ", prev_cnf)
            allSolutions = SATsolver(prev_cnf)
            minSolutinos = getMinSolutions(allSolutions, prev_cnf)
            print("New min solutions: ", minSolutinos)
            new_to_test = []
            for s in minSolutinos:
                for ft in fault_type:  ## check fault type for services
                    fault_sce = [s, ft]
                    new_to_test.append([s, ft])
            print("New to test FS list: ", new_to_test)
            print("Calling to recursive_solve ........")
            recursive_solve(prev_cnf, fault_type, new_to_test, request_type_tested_FS, error_FS, services_pq, services_dict, request_type, services_total_FS_dict, services_error_FS_dict, error_IP_prune, ifSort=ifSort, ifPrune=ifPrune)
            prev_cnf.pop()
            print("Pop last element in prev cnf: ", prev_cnf)
    return

if __name__ == '__main__':
    ########for testing#######
    # cnf = [[1,2,3,4],[1,3]]
    # print(SATsolver(cnf))
    # services = ['api', 'reating', 'review', 'replay', 'test']
    # services_dict = createServiceDict(services)
    # services_pq = {'api': 0.5, 'reating': 1.0, 'review': 1.0, 'replay': 0, 'test': 0}
    # to_test_FS = [[[1], 'abort'], [[1], 'delay'], [[2], 'abort'], [[2], 'delay']]
    # sortByPriority (services_pq, to_test_FS, services_dict)
    # request_type_class = [["api", "reating", "review", "replay"]]
    # request = ["api", "reating", "review", "replay"]
    # print(randomPriority({'api': 1.0, 'reating': 0, 'review': 1.0, 'replay': 1.0, 'test': 0}))
    # request_type_class = get_request_type_traces()

    request_type_class = []
    main(request_type_class, ifRandom = True)
    
