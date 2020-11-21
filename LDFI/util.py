# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 00:38:07 2020

@author: Ling
"""
import os
import time
import subprocess, json
import logging
import platform
from pathlib import Path
from datetime import datetime, timedelta

requests = ['type_admin_get_orders', 'type_admin_get_route', 
            'type_admin_get_travel', 'type_admin_login',
            'type_cheapest_search', 'type_food_service', 'type_preserve',
            'type_user_login']

jmeter_path = Path('./jmeter/apache-jmeter-5.3/bin')
request_to_entry_service = {'type_admin_get_orders' : 'ts-admin-order-service',
                            'type_admin_get_route':'ts-admin-route-service',
                            'type_admin_get_travel': 'ts-admin-travel-service',
                            'type_admin_login':'ts-admin-user-service',
                            'type_cheapest_search':'ts-travel-plan-service',
                            'type_food_service': 'ts-food-map-service',
                            'type_preserve' : 'ts-preserve-service',
                            'type_user_login': 'ts-user-service'}
jmeter_folder = Path('./jmeter')
request_folder = os.path.join(jmeter_folder, 'jmeter_code')
request_log_folder = os.path.join(request_folder, 'logs')

def inject_and_get_trace(list_service, fault, request_type):
    #_inject_failure
    
    try:
        request_result = _get_request_by_type(request_type, False)
        if not request_result:
            return None
    except:
        print('keep going and look at log later')
    
        
def get_request_type_traces():
    traces = dict()
    #jmx_path = r'C:\Users\Ling\OneDrive\Documents\Brown-DESKTOP-8B9G99R\ds-microservices\final-project\jmeter-data\jmeter_tests'
    
    for request in requests:
        #request_path = os.path.join(jmx_path, request+'.jmx')
        services = _get_request_by_type(request, True)
        services = list(set(services))
        traces[request] = services
    return traces

def _get_result_from_log(file_path):
    # get result for file
    success_index = 7
    success = True
    with open(file_path, "r") as file:
        lines = file.readlines() 
        for line in lines[1:]:
            contents = line.split(',')
            success = success and contents[success_index] == 'true'
    if os.path.exists(file_path) and success:
        os.remove(file_path) # if there is no error, remove log

    return success



def _get_request_by_type(request_type, firt_run):
    
    request_file = os.path.join(request_folder, request_type +'.jmx')
    request_log = os.path.join(request_log_folder, request_type +'.log')
    if platform.system() == 'Linux':
        jmeter_exec = os.path.join(jmeter_path, 'jmeter.sh')
        jmeter_exec = './' + jmeter_exec
    else:
        jmeter_exec = os.path.join(jmeter_path, 'jmeter.bat')
    command = '{} -n -t {} -l {}'.format(jmeter_exec, request_file, request_log)
    #python_command = 'jmeter.bat -n -t C:\Users\Ling\OneDrive\Documents\Brown-DESKTOP-8B9G99R\ds-microservices\final-project\jmeter-data\jmeter_tests\type_admin_get_orders.jmx  -l C:\Users\Ling\OneDrive\Documents\Brown-DESKTOP-8B9G99R\ds-microservices\final-project\jmeter-data\jmeter_tests\logs\test1.txt'
    # run_command
    os.popen(command)
    time.sleep(5)
    success = _get_result_from_log(request_log)
    
    if not success:
        if firt_run:
            # raise error
            logging.error("Error in init first time run _get_request_by_type")
            raise Exception('Unexpected failure in init, please check!!!!!!!!')
        else:
            # log and return None
            # log
            logging.info("Failure happen and return None")
            return None
    else:
        # return set of services 
        # get trace from jaeger
        # extract services set
        return _get_trace_from_jaeger(request_type)
        
def _get_trace_from_jaeger(request_type):
    #api_command = 'http://34.74.108.241:32688/api/traces?end=1605986668774000&limit=20&lookback=1h&maxDuration&minDuration&service=ts-basic-service&start=1605983068774000'
    limit_number = 4
    entry_service_name = request_to_entry_service[request_type]
    end_time = _get_milliseconds_time(datetime.now())
    start_time = _get_milliseconds_time(datetime.now() - timedelta(seconds = 20))
    api_url = 'http://34.74.108.241:32688/api/traces?end={}&limit={}&lookback=1h&maxDuration&minDuration&service={}&start={}'\
            .format(end_time, limit_number, entry_service_name, start_time)
    command = 'curl -s \'{}\''.format(api_url)
    proc = subprocess.Popen(command, shell=True,  stdout=subprocess.PIPE)
    json_data, error = proc.communicate()
    return _extract_services_set(json_data, False)
         
    
def _get_milliseconds_time(date_time):
    return int(date_time.timestamp() * 1000000)

def _extract_services_set(j, bfile = False):
    # this function takes path or json data as input. example json can get from either list of traces or single trace json
    # 'http://34.74.108.241:32688/api/traces?end=1605493832031000&limit=20&lookback=1h&maxDuration&minDuration&service=ts-train-service&start=1605490232031000' 
    # return list of set of services for each trace in that json
    if bfile:
        with open(j) as f:
            data = json.load(f)['data']
    else:
        data = json.load(j)
        print(data)
        data = data['data']
        
    result = list()
    for trace in data:
        services_set = set()
        processes = trace['processes']
        for service in processes:
            services_set.add(processes[service]['serviceName'])
        result.append(services_set)
    return result

def _inject_failure(service_name, fault):
    # istio
    pass

get_request_type_traces()
        
        