import pycosat
from bidict import bidict
import random
from itertools import chain
import sys
import copy
from util import get_request_type_traces, inject_and_get_trace

#counter
COUNTER = 0

# given the list of all the services, map each services to unique id
#def createServiceDict(servicesList):

# given a set of services, using its corresponding id to a cnf
def covertCNF(user_request, services_dict):
    print("hi convertCNF ", user_request)
    print("services_dict ", services_dict)
    cnf = []
    for s in user_request:
        cnf.append(services_dict[s])
    print("convert cnf:", cnf)
    return cnf
    

#given cnf, using pycosat to generate all the solutions
#return all possible solutions
def SATsolver(cnf, isCNF = True):
    print("sat is solving.........." , cnf)
    cnf_dup = copy.deepcopy(cnf)
    universe = list(set(x for l in cnf_dup for x in l))
    print("universe ", universe)
    temp_dict = bidict()
    i = 1
    for s in universe:
        temp_dict.update([(s, i)])
        i+=1
    print("temp_ dict: ", temp_dict)
    # print(cnf, "                         ", cnf_dup)
    for c in cnf_dup:
        for s, index in zip(c, range(len(c))):
            c[index] = temp_dict[s]
    # print(cnf_dup)
    # print(cnf, "                        ", cnf_dup)

    if isCNF == False:
        allSolutions = list(pycosat.itersolve([cnf_dup], prop_limit=50))
        print(allSolutions)
        res = []
        for s in allSolutions:
            temp = [item for item in s if item > 0]
            res.append(temp)
        res = sorted(res, key=len)
        print(res)
    else:
        allSolutions = list(pycosat.itersolve(cnf_dup, prop_limit=50))
        print("all solutions1:", allSolutions)
        res = []
        for s in allSolutions:
            temp = [item for item in s if item > 0]
            res.append(temp)
        res = sorted(res, key=len)
        # print("all solutions: ",res)
    for c in res:
        print(c)
        for s, index in zip(c, range(len(c))):
            c[index] = temp_dict[:s]
    # print(cnf, " ", cnf_dup)
    print("all solutions2: ",res)
    return res

#remove the negative vaules, sort by size -> remove from universe -> get the min solutions
def getMinSolutions(solutions, cnf):
    minSolutions = []
    # cnf = set(cnf)
    universe = set(x for l in cnf for x in l)
    print("input cnf in getMinSolutions: " ,cnf)
    unique_values = set(chain(*cnf))
    while unique_values:
        for s in solutions:
            covered = unique_values & set(s)
            if covered:
                minSolutions.append(s)
                # unique_values = unique_values.difference(covered)
                unique_values -= covered
    # for s in solutions:
    #     if set(s).issubset(unique_values):
    #         minSolutions.append(s)
    #         unique_values = unique_values.difference(set(s))

    print("getMinSolutions: ", minSolutions)

    # print("input cnf in getMinSolutions: " ,cnf)
    # universe_values = set(chain(*cnf))
    # while unique_values:
    #     # best = None
    #     set_covered = set()
    #     for sol in solutions:
    #         covered = unique_values & sol
    #         if len(covered) <= len(set_covered):
    #             set_covered = covered
    #             # best = covered
    #     unique_values -= set_covered
    #     minSolutions.append()
    # print("getMinSolutions: ", minSolutions)
    return minSolutions

def createServiceDict(services):
    services_dict = bidict()
    i = 1
    for s in services:
        services_dict.update([(s, i)])
        i+=1
    print("service dict: ", services_dict)
    return services_dict

def main(request_type_class, ifRandom = False):
    # preprocess -> create dict for all services (sign a ID to each of services)
    services = ['api', 'reating', 'review', 'replay', 'test']
    ########testing
    services = ['ts-food-service', 'ts-notification-service', 'ts-seat-service', 'ts-price-service', 'ts-basic-service', 'ts-station-service', 'ts-route-service', 'ts-config-service', 'ts-order-service', 'ts-order-other-service', 'ts-train-service', 'ts-contacts-service', 'ts-consign-price-service', 'ts-user-service', 'ts-travel-service', 'ts-assurance-service', 'ts-security-service', 'ts-preserve-service', 'ts-consign-service', 'ts-ticketinfo-service']
    fault_type = ['abort', 'delay']
    # injection_sec = []

    services = [ 'ts-user-service', 'ts-auth-service', 'ts-inside-payment-service', 'ts-preserve-other-service', 'ts-rebook-service', 'ts-route-service', 'ts-ticketinfo-service', 'ts-admin-travel-service', 'ts-food-map-service', 'ts-train-service', 'ts-admin-user-service', 'ts-cancel-service', 'ts-ticket-office-service', 'ts-station-service', 'ts-travel-service', 'ts-execute-service', 'ts-preserve-service', 'ts-payment-service', 'ts-contacts-service', 'ts-basic-service', 
    'ts-seat-service', 'ts-admin-route-service', 'ts-admin-basic-info-service', 'ts-travel2-service', 'ts-travel-plan-service', 'ts-consign-price-service', 'ts-security-service', 'ts-verification-code-service', 'ts-route-plan-service', 'ts-price-service', 'ts-order-service', 'ts-assurance-service', 'ts-news-service', 'ts-notification-service', 'ts-config-service', 'ts-food-service', 'ts-consign-service', 'ts-voucher-service', 'ts-admin-order-service', 'ts-order-other-service', 'ts-ui-dashboard', ]
    services = [ch+'.default' for ch in services]
    #set a unique id <-> service dict
    # services_dict = bidict()
    # i = 1
    # for s in services:
    #     services_dict.update([(s, i)])
    #     i+=1
    # print(services_dict)
    services_dict = createServiceDict(services)
    # temp = 'ts-food-service'
    # print("test bidict: ", services_dict[temp])
    # temp=1
    # print("test bidict: ",services_dict[:temp])
    
    # D=bidict({'a':1})
    # D.update([('four', 4)])
    # print(D[:4])
    # thisdict = dict.fromkeys(services)
    # print(thisdict)    

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

    # phase 1: random select from integration tests
    # for each request in request_type_class (from integration tests), check the eqv class

    ######for testing
    # request_type_class = {"login" : ['api', 'reating']}
    # request_type_class = {"login" : ['api', 'reating', 'review', 'replay']}

    # request_type_class = {"preserve" : ['ts-food-service', 'ts-notification-service', 'ts-seat-service', 'ts-price-service', 'ts-basic-service', 'ts-station-service', 'ts-route-service', 'ts-config-service', 'ts-order-service', 'ts-order-other-service', 'ts-train-service', 'ts-contacts-service', 'ts-consign-price-service', 'ts-user-service', 'ts-travel-service', 'ts-assurance-service', 'ts-security-service', 'ts-preserve-service', 'ts-consign-service', 'ts-ticketinfo-service']}
    # request_type_class = {"preserve" : ['ts-food-service', 'ts-notification-service', 'ts-seat-service', 'ts-price-service']}

    if ifRandom:
        request_type_class = get_request_type_traces()

        #equvient request class set -> group by the nodes(services) && the order(dependency) --> no dependency ??
        request_class = [] #gobal var?

        all_request_types = request_type_class.keys()

        request_type_tested_FS = dict((el,[]) for el in all_request_types)
        print("request_type_tested_FS: ", request_type_tested_FS)

        error_FS = dict((el,[]) for el in all_request_types)

        services_total_FS_dict = dict((el,0) for el in services)
        print("services_total_FS_dict: ", services_total_FS_dict)

        services_error_FS_dict = dict((el,0) for el in services)

        services_pq = dict((el,0) for el in services)

        for request_type, request in request_type_class.items():
            injection_sce = []
            print("request type: ",request_type, ", request: ", request)
            if sorted(request) in request_class:
                continue
            else:
                request_class.append(sorted(request))
            
            print("request_class: ", request_class) ##request class duplicate???? not necessary???

            clause = covertCNF(request, services_dict)
            prev_cnf = []
            prev_cnf.append(clause)
            print("prev_cnf: ", prev_cnf)

            to_test_FS = []
            error_IP_prune = []  

            #solve min solutions --> injection points --> then combine with fault
            allSolutions = SATsolver(prev_cnf)
            minSolutinos = getMinSolutions(allSolutions, prev_cnf)
            for s in minSolutinos:
                for ft in fault_type:  ## check fault type for services??
                    fault_sce = [s, ft]
                    to_test_FS.append([s, ft])

            recursive_solve(prev_cnf, fault_type, to_test_FS, request_type_tested_FS, error_FS, services_pq, services_dict, request_type, services_total_FS_dict, services_error_FS_dict, error_IP_prune, ifPrune=False)

    else:

        subset1 = ['type_admin_get_orders', 'type_simple_search', 'type_admin_get_route']
        subset2 = ['type_admin_get_travel', 'type_admin_login',
            'type_cheapest_search', 'type_food_service', 'type_preserve',
            'type_user_login']
        request_type_class = get_request_type_traces()
        request_type_class_subset1 = get_request_type_traces(subset1)
        request_type_class_subset2 = get_request_type_traces(subset2)

        #equvient request class set -> group by the nodes(services) && the order(dependency) --> no dependency ??
        request_class = [] #gobal var?

        all_request_types = request_type_class.keys()

        request_type_tested_FS = dict((el,[]) for el in all_request_types)
        print("request_type_tested_FS: ", request_type_tested_FS)

        error_FS = dict((el,[]) for el in all_request_types)

        services_total_FS_dict = dict((el,0) for el in services)
        print("services_total_FS_dict: ", services_total_FS_dict)

        services_error_FS_dict = dict((el,0) for el in services)

        services_pq = dict((el,0) for el in services)

        for request_type, request in request_type_class_subset1.items():
            injection_sce = []
            print("request type: ",request_type, ", request: ", request)
            if sorted(request) in request_class:
                continue
            else:
                request_class.append(sorted(request))
                # print(request_class)
            
            print("request_class: ", request_class) ##request class duplicate???? not necessary???

            #covert current request (input a request) to CNF
            # prev_cnf = covertCNF(request, services_dict)
            # print("prev_cnf: ", prev_cnf)

            #solve min solutions --> injection points --> then combine with fault
            # allSolutions = SATsolver(prev_cnf, isCNF=False)
            # print(type(allSolutions))
            # minSolutinos = getMinSolutions(allSolutions, prev_cnf)
            # # minSolutinos = [[1], [2], [3, 4]]
            # test_sce = []
            # for s in minSolutinos:
            #     for ft in fault_type:  ## check fault type for services??
            #         fault_sce = [s, ft]
            #         if fault_sce not in injection_sce:
            #             injection_sce.append([s, ft])
            #             test_sce.append(fault_sce)
            # print(test_sce)
            # rand = random.choice(test_sce)
            # print("random: ", rand, services_dict[:rand[0][0]])



            ##########################################################
            #covert current request (input a request) to CNF
            
            ##########test
            # request = ['api', 'reating']
            clause = covertCNF(request, services_dict)
            prev_cnf = []
            prev_cnf.append(clause)
            print("prev_cnf: ", prev_cnf)

            to_test_FS = []
            # request_type_tested_FS[request_type].append([]) 
            # error_FS = []
            # services_pq = []
            error_IP_prune = []  #???/

            #solve min solutions --> injection points --> then combine with fault
            allSolutions = SATsolver(prev_cnf)
            minSolutinos = getMinSolutions(allSolutions, prev_cnf)
            for s in minSolutinos:
                for ft in fault_type:  ## check fault type for services??
                    fault_sce = [s, ft]
                    to_test_FS.append([s, ft])

            recursive_solve(prev_cnf, fault_type, to_test_FS, request_type_tested_FS, error_FS, services_pq, services_dict, request_type, services_total_FS_dict, services_error_FS_dict, error_IP_prune)
            
            #random give a test_sec to do fault injection
            # injection_res = inject_and_get_trace(services, fault, classtype)
            # injection_res = covertCNF(injection_res, services_dict)
            # injection_res = [1,2,3,5]

            #update pq

            #pruning
        ##########################subset2
        for request_type, request in request_type_class_subset2.items():
            injection_sce = []
            print("request type: ",request_type, ", request: ", request)
            if sorted(request) in request_class:
                continue
            else:
                request_class.append(sorted(request))
                # print(request_class)
            
            print("request_class: ", request_class) ##request class duplicate???? not necessary???

            #covert current request (input a request) to CNF
            # prev_cnf = covertCNF(request, services_dict)
            # print("prev_cnf: ", prev_cnf)

            #solve min solutions --> injection points --> then combine with fault
            # allSolutions = SATsolver(prev_cnf, isCNF=False)
            # print(type(allSolutions))
            # minSolutinos = getMinSolutions(allSolutions, prev_cnf)
            # # minSolutinos = [[1], [2], [3, 4]]
            # test_sce = []
            # for s in minSolutinos:
            #     for ft in fault_type:  ## check fault type for services??
            #         fault_sce = [s, ft]
            #         if fault_sce not in injection_sce:
            #             injection_sce.append([s, ft])
            #             test_sce.append(fault_sce)
            # print(test_sce)
            # rand = random.choice(test_sce)
            # print("random: ", rand, services_dict[:rand[0][0]])



            ##########################################################
            #covert current request (input a request) to CNF
            
            ##########test
            # request = ['api', 'reating']
            clause = covertCNF(request, services_dict)
            prev_cnf = []
            prev_cnf.append(clause)
            print("prev_cnf: ", prev_cnf)

            to_test_FS = []
            # request_type_tested_FS[request_type].append([]) 
            # error_FS = []
            # services_pq = []
            error_IP_prune = []  #???/

            #solve min solutions --> injection points --> then combine with fault
            allSolutions = SATsolver(prev_cnf)
            minSolutinos = getMinSolutions(allSolutions, prev_cnf)
            for s in minSolutinos:
                for ft in fault_type:  ## check fault type for services??
                    fault_sce = [s, ft]
                    to_test_FS.append([s, ft])

            recursive_solve(prev_cnf, fault_type, to_test_FS, request_type_tested_FS, error_FS, services_pq, services_dict, request_type, services_total_FS_dict, services_error_FS_dict, error_IP_prune, ifSort=True)

    global COUNTER 
    print("**************************************************************************************************")
    print(COUNTER)
    
    #phase 1: send the injection_sec to istio to random choose and do injection

    ############################################################################

    ## test min solutions
    # test1 = SATsolver([[1, 2,3],[1,2,4]], isCNF=True)
    # print("test min solution 1: ", test1)
    # test1 = getMinSolutions(test1, [1,2,3,4])
    # print("test min solution 1: ", test1)

    # test2 = SATsolver([[1,3],[1,4],[2,3],[2,4]], isCNF=True)
    # print("test min solution 2: ", test2)
    # test2 = getMinSolutions(test2, [1,2,3,4])
    # print("test min solution 1: ", test2)

        #(fault type for each service, replay corresponding request)

def sortByPriority (services_pq, to_test_FS, services_dict):
    print(to_test_FS)
    for i in range(len(to_test_FS)):
        fs = to_test_FS[i]
        value = 0
        print(fs)
        for s in fs[0]:
            print(s)
            print(s, " ", services_pq[services_dict[:s]])
            value = value + services_pq[services_dict[:s]]
        value /= len(fs[0])
        to_test_FS[i].append(value)
    to_test_FS.sort(key = lambda x: -x[2]) 
    for i in range(len(to_test_FS)):
        to_test_FS[i].pop()
    print(to_test_FS)
    return to_test_FS

def randomPriority(services_pq):
    print(services_pq)
    for k, v in services_pq.items():
        if v == 0:
            services_pq[k] = random.random()
    
    return services_pq


def recursive_solve(prev_cnf, fault_type, to_test_FS, request_type_tested_FS, error_FS, services_pq, services_dict, request_type, services_total_FS_dict, services_error_FS_dict, error_IP_prune, ifSort = False, ifPrune=True):
    global COUNTER 
    COUNTER += 1
    if ifSort:
        services_pq = randomPriority(services_pq) ##random from not reached services, whether add a small random value for other services????
        to_test_FS = sortByPriority(services_pq, to_test_FS, services_dict)
    
    for rand_curr_FS in to_test_FS: #random ??
        # for rand_curr_FS in to_test_FS: #random ??
        # rand_curr_FS = random.choice(to_test_FS)
        # to_test_FS.remove(rand_curr_FS)
        print()
        print('-------------------------------------------------------')
        print("to test: ", to_test_FS)
        print("curr FS: ", rand_curr_FS)
        #check duplicate
        if rand_curr_FS in request_type_tested_FS[request_type]: #check if this FS is already tested for this request type
            continue
        if rand_curr_FS in error_FS[request_type]: #check if this FS is already tested for this request type and find a bug --> duplicate??
            continue
        
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


        #pruning ???  --> for each single point in IPs, if it already exixts in error
        # ifPrune = False
        # for ip in rand_curr_FS[0]:
        #     temp = []
        #     temp.append(ip)
        #     # if temp in error_IP_prune:
        #     #     ifPrune = True
        #     if temp in pruning:
        #         ifPrune = True
        # if ifPrune:
        #     print("it pruned!! ")
        #     continue

        inject_points = []
        for i in rand_curr_FS[0]:
            print("injection point ID: ",i)
            service_name = services_dict[:i]
            print("injection point service_name: ", service_name)
            inject_points.append(service_name)
            services_total_FS_dict[service_name] += 1  #append() or just add 1   ####update pq
        print("udpate total: ", services_total_FS_dict)
        # print("udpate error: ", services_error_FS_dict)
        
        new_call_graph = inject_and_get_trace(inject_points, rand_curr_FS[1], request_type)
        print("new call graph: ", new_call_graph)

        #handle exception from inject and get trace??
        request_type_tested_FS[request_type].append(rand_curr_FS)

        # to_test_FS.remove(rand_curr_FS)

        if not new_call_graph:  #find a service error --> detect a bug
            print("new call graph is null, find bug here!")
            error_FS[request_type].append(rand_curr_FS)
            error_IP_prune.append(rand_curr_FS[0])
            for s in inject_points:
                services_error_FS_dict[s] += 1
                services_pq[s] = services_error_FS_dict[s] / services_total_FS_dict[s]  #update priority for each services
            print("udpate error: ", services_error_FS_dict)
            print("udpate total: ", services_total_FS_dict)
            print("updated service priority (find bug): ", services_pq)
            # continue
        else:
            #for good outcome, update priority ???
            for s in inject_points:
                services_pq[s] = services_error_FS_dict[s] / services_total_FS_dict[s]  #update priority for each services
            print("udpate error: ", services_error_FS_dict)
            print("udpate total: ", services_total_FS_dict)
            print("updated service priority (new call graph): ", services_pq)

            new_clause = covertCNF(new_call_graph, services_dict)
            print("new clause: ", new_clause)
            prev_cnf.append(new_clause)
            print("new cnf: ", prev_cnf)
            allSolutions = SATsolver(prev_cnf)
            minSolutinos = getMinSolutions(allSolutions, prev_cnf)
            print("new min solutions: ", minSolutinos)
            new_to_test = []
            for s in minSolutinos:
                for ft in fault_type:  ## check fault type for services??
                    fault_sce = [s, ft]
                    new_to_test.append([s, ft])
            print("new to test list: ", new_to_test)
            print("call recursive solve ........")
            recursive_solve(prev_cnf, fault_type, new_to_test, request_type_tested_FS, error_FS, services_pq, services_dict, request_type, services_total_FS_dict, services_error_FS_dict, error_IP_prune, ifSort=ifSort, ifPrune=ifPrune)
            prev_cnf.pop()
            print("pop last element in prev cnf: ", prev_cnf)
    return

# def inject_and_get_trace(inject_points, fault_type, request_type):
#     temp = input("Enter something: ")
#     print(temp)
#     services = temp.split()
#     graph = []
#     for s in services:
#         graph.append(s)
#     return graph
#     # return ['review']




# def recursive_solve2(prev_cnf, fault_type, to_test_FS, tested_FS, error_FS, services_pq, services_dict, request_type, services_total_FS_dict, services_error_FS_dict):
#     if not to_test_FS:
#         return
#     else:
#         rand_curr_FS = random.choice(to_test_FS)
#         inject_points = []
#         for i in rand_curr_FS[0]:
#             service_name = services_dict[:rand_curr_FS[0][i]]
#             inject_points.append(service_name)
#             services_total_FS_dict[service_name] += 1  #append() or just add 1
#         new_call_graph = inject_and_get_trace(inject_points, rand_curr_FS[1], request_type)
#         tested_FS.append(rand_curr_FS)
#         to_test_FS.remove(rand_curr_FS)
#         if not new_call_graph:
#             error_FS.append(rand_curr_FS)
#             for s in inject_points:
#                 services_error_FS_dict[s] += 1
#                 services_pq[s] = services_error_FS_dict[s] / services_total_FS_dict[s]
#             return
#         else:
#             new_clause = covertCNF(new_call_graph, services_dict)
#             prev_cnf.append(new_clause)
#             recursive_solve(prev_cnf, fault_type, to_test_FS, tested_FS, error_FS, services_pq, services_dict, request_type, services_total_FS_dict, services_error_FS_dict)

if __name__ == '__main__':
    cnf = [[1,2,3,4],[1,3]]
    print(SATsolver(cnf))
    services = ['api', 'reating', 'review', 'replay', 'test']
    services_dict = createServiceDict(services)
    services_pq = {'api': 0.5, 'reating': 1.0, 'review': 1.0, 'replay': 0, 'test': 0}
    to_test_FS = [[[1], 'abort'], [[1], 'delay'], [[2], 'abort'], [[2], 'delay']]
    # sortByPriority (services_pq, to_test_FS, services_dict)
    # request_type_class = [["api", "reating", "review", "replay"]]
    # request = ["api", "reating", "review", "replay"]
    print(randomPriority({'api': 1.0, 'reating': 0, 'review': 1.0, 'replay': 1.0, 'test': 0}))

    # request_type_class = get_request_type_traces()
    request_type_class = []
    main(request_type_class, ifRandom = False)
    
