# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 17:19:16 2020

This file is a baseline that uses semi-random fault injection. 
There are two different random algorithms.
First is to randomly get services without type and expore both fault type.
Second is to randomly get services with fault types.

Both  methods are semi-random which starts with combination of length r = 1. 
If does not fail all 9 services for current length after exploring all combination,
then increment length r until explore all combination.


For all services, system starts to random from combinnation length r = 1


@author: Xiling Zhang, Qingyi Lu
"""
from util import get_request_type_traces, inject_and_get_error_requests, inject_and_get_error_requests2
import random

from itertools import combinations
requests = ['type_admin_get_route', 'type_food_service', 'type_simple_search', 'type_admin_get_orders', 'type_admin_get_travel', 'type_admin_login',
                'type_cheapest_search',  'type_preserve', 'type_user_login']

microservices = ['ts-user-service', 'ts-auth-service', 'ts-inside-payment-service', 'ts-preserve-other-service', 'ts-rebook-service', \
                 'ts-route-service', 'ts-ticketinfo-service', 'ts-admin-travel-service', 'ts-food-map-service', 'ts-train-service', \
                     'ts-admin-user-service', 'ts-cancel-service', 'ts-ticket-office-service', 'ts-station-service', 'ts-travel-service', \
                         'ts-execute-service', 'ts-preserve-service', 'ts-payment-service', 'ts-contacts-service', 'ts-basic-service', \
                             'ts-seat-service', 'ts-admin-route-service', 'ts-admin-basic-info-service', 'ts-travel2-service', \
                                 'ts-travel-plan-service', 'ts-consign-price-service', 'ts-security-service', 'ts-verification-code-service', \
                                     'ts-route-plan-service', 'ts-price-service', 'ts-order-service', 'ts-assurance-service', 'ts-news-service',\
                                         'ts-notification-service', 'ts-config-service', 'ts-food-service', 'ts-consign-service', 'ts-voucher-service', \
                                             'ts-admin-order-service', 'ts-order-other-service']
microservices = [ch+'.default' for ch in microservices]
microservices_with_faults = []
for ch in microservices:
    microservices_with_faults.append([ch, 'delay'])
    microservices_with_faults.append([ch, 'abort'])

def random_combination(iterable, r):
    "Random selection from itertools.combinations(iterable, r)"
    pool = tuple(iterable)
    n = len(pool)
    indices = sorted(random.sample(range(n), r))
    return tuple(pool[i] for i in indices)

def random_services_with_fault():
    # random get 1 service with 1 fault
    get_request_type_traces()
    counter = 0
    r = 0
    comb = []
    p = 0
    while len(requests) > 0:        
        # random get one from combination
        if p == len(comb):
            r += 1
            
            if r > len(microservices):
                print('reach all combinations, cannot finish....')
                break
            # get combination and random. generator random? 
            comb = list(combinations(microservices_with_faults, r))
            random.shuffle(comb)
            p = 0
            
        services = comb[p]
        p += 1
        errored_services = inject_and_get_error_requests2(services, requests)
        
        for ch in errored_services:
            if ch in requests:
                requests.remove(ch)
            else:
                print('unexpected service: ', ch)

        counter += 1 # add 2 for delay and abort
        print('counter: ', counter)

    print('finished. Nnumber of injections: ', counter)

def random_services_from_r1():
    # random starting with r = 1 for combination
    get_request_type_traces()
    counter = 0
    r = 0
    comb = []
    p = 0
    while len(requests) > 0:        
        # random get one from combination
        if p == len(comb):
            r += 1
            
            if r > len(microservices):
                print('reach all combinations, cannot finish....')
                break
            # get combination and random. generator random? 
            comb = list(combinations(microservices, r))
            random.shuffle(comb)
            p = 0
            
        services = comb[p]
        p += 1
        # try:
        #     services = next(comb)
        # except StopIteration:
        #     print('combination for length ', r, ' ends. +1..')
        #     r += 1
        #     if r > len(microservices):
        #         print('reach all combinations, cannot finish....')
        #     comb = combinations(microservices, r)
        #     continue
 
        # inject failures
        # get request types
        errored_services = inject_and_get_error_requests(services, 'delay')
        errored_services = inject_and_get_error_requests(services, 'abort')
        
        for ch in errored_services:
            if ch in requests:
                requests.remove(ch)
            else:
                print('unexpected service: ', ch)

        counter += 2 # add 2 for delay and abort
        print('counter: ', counter)

    print('finished. Nnumber of injections: ', counter)
# two way for random injection. inject with pure 
def main():

    # init run get requests traces 
    random_services_with_fault()
    

if __name__ == '__main__':
    # pure random
    main()
