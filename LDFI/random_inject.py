# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 17:19:16 2020

This file is a baseline that uses semi-random fault injection. 
For all services, system starts to random from combinnation length r = 1


@author: Ling
"""
from util import get_request_type_traces, inject_and_get_error_requests

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
    
    
def main():

    # init run get requests traces 
    get_request_type_traces()
    counter = 0
    r = 1
    comb = combinations(microservices, r)
    while len(requests) > 0:        
        # random get a combination
        try:
            services = next(comb)
        except StopIteration:
            print('combination for length ', r, ' ends. +1..')
            r += 1
            if r > len(microservices):
                print('reach all combinations, cannot finish....')
            comb = combinations(microservices, r)
            continue
 
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

if __name__ == '__main__':
    # pure random
    main()