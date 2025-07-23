#!/usr/bin/env python3
import sys
import yaml
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.topo import Topo


from ortools.linear_solver import pywraplp

routers = {}
mininet_routers={}
hosts={}
mininet_hosts={}
subnets={}
links={}
demands=[]

def parse_yaml(data):
    global routers,hosts,subnets,links, demands
    # Get routers
    for router_name, interfaces in data.get("routers", {}).items():
        routers[router_name] = {}
        for iface, config in interfaces.items():
            routers[router_name][iface] = {
                "address": config["address"],
                "mask": config["mask"],
                "cost": config.get("cost", 1)
            }
    #Get hosts
    for host_name, interfaces in data.get("hosts", {}).items():
        hosts[host_name] = {}
        for iface, config in interfaces.items():
            hosts[host_name][iface] = {
                "address": config["address"],
                "mask": config["mask"]
            }
    
    #Get demands
    demands=data["demands"]

    #Calculate subnets
    for router,interfaces in routers.items():
        for interface,config in interfaces.items():
            subnet= get_subnet(config["address"],config["mask"])
            if(subnet not in subnets):
                subnets[subnet]={}
                subnets[subnet]["routers"]=[router]
                subnets[subnet]["cost"]=config["cost"]
                subnets[subnet]["hosts"]=[]
                subnets[subnet]["routers-interface"]=[[router,interface]]

            else:
                subnets[subnet]["routers-interface"].append([router,interface])
                subnets[subnet]["routers"].append(router)
                if(subnets[subnet]["cost"]==1):
                    subnets[subnet]["cost"]=config["cost"]

    
    for host,interfaces in hosts.items():
        for config in interfaces.values():
            subnet= get_subnet(config["address"],config["mask"])
            subnets[subnet]["hosts"].append(host)

    #Calculate links
    for router in routers:
        for subnet in subnets:
            if router in subnets[subnet]["routers"]:
                for other_router in subnets[subnet]["routers"]:
                    if router<other_router:
                        links[router,other_router]=subnets[subnet]["cost"]

def transform_binary_string(s):
    i = 0
    res=''
    while(len(s)<32):
        s+='0'
    while(len(s)-i-8>=0):
        res+=str(int(s[i:i+8],2))
        if(len(s)-i-8!=0):
            res+='.'
        i+=8
    return res



class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        # Enable forwarding on the router
        self.cmd('sysctl net.ipv4.ip_forward=1')
        # Enable MPLS  
        self.cmd('modprobe mpls_router')
        self.cmd('modprobe mpls_iptunnel')
        self.cmd('sysctl -w net.mpls.platform_labels=1000000')


    def terminate( self ):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

def ip_to_bits(ip:str)-> str:
    octets = ip.split('.')
    bits = ''.join(f"{int(octet):08b}" for octet in octets)
    return bits

def get_subnet(ip :str, mask :str) -> str:
    subnet=""
    bits_ip=ip_to_bits(ip)
    bits_mask=ip_to_bits(mask)
    for i in range(32):
        if(bits_mask[i]=='1'):
            subnet += bits_ip[i]
        else:
            break
    return subnet

def calculate_path(router:str,subnet:str, router_connection:dict) ->str:
    global routers, mininet_routers, hosts, mininet_hosts, subnets
    if subnet in router_connection[router]["subnets"]:
        return router    
    seen=[]
    temp_router_connection=router_connection.copy()
    to_expand=[]
    to_expand.append([router,'',0])

    while len(to_expand)>0:
        to_expand=sorted(to_expand, key=lambda x: x[2])
        candidate=to_expand[0]
        if subnet in temp_router_connection[candidate[0]]["subnets"]:
            return candidate[1]
        for connection in temp_router_connection[candidate[0]]["connections"]:
            if connection[0] not in seen:
                if(candidate[1]!=''):
                    to_expand.append([connection[0],candidate[1],connection[2]+candidate[2]])
                else:
                    to_expand.append([connection[0],connection[1],connection[2]+candidate[2]])
        seen.append(candidate[0])
        to_expand.pop(0)



    return router







def print_help():
    print("""
usage: best_goodput.py [-h] [-p] [-l] definition
          
A tool to define the emulation of a network configured to achieve the best overall
goodput under a given set of flow demands.
          
positional arguments:
    definition the definition file of the network and flow demands in YAML
options:
    -h, --help show this help message and exit
    -p, --print the optimal goodput for each flow and exit
    -l, --lp print the definition of the optimization problem in CPLEX LP format
    """)
    
def print_problem(yamlFileName):
    global routers,hosts,subnets,links, demands
    with open(yamlFileName) as f:
        data = yaml.safe_load(f)
        parse_yaml(data)
    
    
    #Print objective function 
    print("Maximize")
    print(" obj: lambda")

    #Print constraint
    print("Subject to")
    for i in range(1,len(demands)+1):
        print(f' o{i}: {demands[i-1]['rate']} lambda - i{i} <= 0')
    #Creating real value constraint
    print(r" \ flow balance for real-value rate variables")
    for i in range(1,len(demands)+1):
        first_time=True
        for router in routers:
            for link in links:
                if router == link[0]:
                    if(first_time):
                        print(f' flow_{router}_ri{i}: ri{i}_{link[1]}{link[0]} - ri{i}_{link[0]}{link[1]}', end="") 
                        first_time=False
                    else:
                        print(f' + ri{i}_{link[1]}{link[0]} - ri{i}_{link[0]}{link[1]}', end="")  
                elif router == link[1]:
                    if(first_time):
                        print(f' flow_{router}_ri{i}: ri{i}_{link[0]}{link[1]} - ri{i}_{link[1]}{link[0]}', end="") 
                        first_time=False
                    else:
                        print(f' + ri{i}_{link[0]}{link[1]} - ri{i}_{link[1]}{link[0]}', end="")  
            for values in subnets.values():
                if(router in values["routers"] and demands[i-1]['src'] in values["hosts"]):
                    if(first_time):
                        print(f' flow_{router}_ri{i}: i{i}', end="")
                        first_time=False
                    else:
                        print(f' + i{i} ',end="")
                elif(router in values["routers"] and demands[i-1]['dst'] in values["hosts"]):
                    if(first_time):
                        print(f' flow_{router}_ri{i}: - i{i}', end="")
                        first_time=False
                    else:
                        print(f' - i{i} ',end="") 
            print("= 0")                
            first_time=True
        print("")
    
    #Creating binary constraint 
    print(r" \ flow balance for indicators, for each flow, for each node")
    for i in range(1,len(demands)+1):
            first_time=True
            for router in routers:
                for link in links:
                    if router == link[0]:
                        if(first_time):
                            print(f' flow_{router}_i{i}: i{i}_{link[1]}{link[0]} - i{i}_{link[0]}{link[1]}', end="") 
                            first_time=False
                        else:
                            print(f' + i{i}_{link[1]}{link[0]} - i{i}_{link[0]}{link[1]}', end="")  
                    elif router == link[1]:
                        if(first_time):
                            print(f' flow_{router}_i{i}: i{i}_{link[0]}{link[1]} - i{i}_{link[1]}{link[0]}', end="") 
                            first_time=False
                        else:
                            print(f' + i{i}_{link[0]}{link[1]} - i{i}_{link[1]}{link[0]}', end="")  
                temp=True
                for values in subnets.values():
                    if(router in values["routers"] and demands[i-1]['src'] in values["hosts"]):
                        print("= -1")
                        temp=False
                        break
                    elif(router in values["routers"] and demands[i-1]['dst'] in values["hosts"]):
                        print("= 1")
                        temp=False
                        break
                if(temp):
                    print("= 0")                
                first_time=True
            print("")
    
    #Input exclusion constraint
    print(r"\ mutual exclusion of incoming into same node, for each flow, for each node")
    for i in range(1,len(demands)+1):
        first_time=True
        for router in routers:
            for link in links:
                if router == link[1]:
                    if(first_time):
                        print(f' in_{router}_i{i}: i{i}_{link[0]}{link[1]}', end="") 
                        first_time=False
                    else:
                        print(f' + i{i}_{link[0]}{link[1]}', end="")  
                elif router==link[0]:
                    if(first_time):
                        print(f' in_{router}_i{i}: i{i}_{link[1]}{link[0]}', end="") 
                        first_time=False
                    else:
                        print(f' + i{i}_{link[1]}{link[0]}', end="")  

            
            if(first_time==False):
                print(" <= 1")
            first_time=True
        print("")

    #Same but for output 
    print(r"\ mutual exclusion of outgoing out of same node, for each flow, for each node")
    for i in range(1,len(demands)+1):
        first_time=True
        for router in routers:
            for link in links:
                if router == link[0]:
                    if(first_time):
                        print(f' out_{router}_i{i}: i{i}_{link[0]}{link[1]}', end="") 
                        first_time=False
                    else:
                        print(f' + i{i}_{link[0]}{link[1]}', end="")  
                elif router==link[1]:
                    if(first_time):
                        print(f' out_{router}_i{i}: i{i}_{link[1]}{link[0]}', end="") 
                        first_time=False
                    else:
                        print(f' + i{i}_{link[1]}{link[0]}', end="")  
            if(first_time==False):
                print(" <= 1")
            first_time=True
        print("")
    #Constraint on total link traffic
    print(r"\ link capacities, for each link")
    first_time=True
    for link,cost in links.items():
        for i in range(1,len(demands)+1):
            if(first_time):
                print(f' {link[0]}{link[1]}_c: ri{i}_{link[0]}{link[1]} + ri{i}_{link[1]}{link[0]}', end="")
                first_time=False
            else:
                print(f' + ri{i}_{link[0]}{link[1]} + ri{i}_{link[1]}{link[0]}', end="")
        print(f'<= {cost}')
        first_time=True
    #Adding constraints on individual variables
    print(r"\ control of real-value flow variables by corresponding indicators, for each flow and link")
    for i in range(1,len(demands)+1):
        for link, cost in links.items():
            print(f' {link[0]}{link[1]}_ci{i} : ri{i}_{link[0]}{link[1]} - {cost} i{i}_{link[0]}{link[1]} <= 0')
            print(f' {link[1]}{link[0]}_ci{i} : ri{i}_{link[1]}{link[0]} - {cost} i{i}_{link[1]}{link[0]} <= 0')
        print("")

    #Bounds on the input variables
    print(r"\ bounds on the input variables")
    print("Bounds")
    for i in range(1,len(demands)+1):
        print(f' i{i}<={demands[i-1]['rate']}')
    print("")
    #Declaring binary variables
    print("Binary")
    for i in range(1, len(demands)+1):
        for link in links:
            print(f' i{i}_{link[0]}{link[1]}')
            print(f' i{i}_{link[1]}{link[0]}')
        print("")
#========================================================================================================================

def solve_problem(yamlFileName, outputModel):
    global routers,hosts,subnets,links, demands
    with open(yamlFileName) as f:
        data = yaml.safe_load(f)
        parse_yaml(data)
    solver = pywraplp.Solver.CreateSolver('CBC')
    var_lambda = solver.NumVar(-solver.infinity(), solver.infinity(),'lambda')
    #Creating obj constraints
    real_variables={}
    bin_variables={}
    for i in range(1,len(demands)+1):
        real_variables[f'i{i}']= solver.NumVar(0, demands[i-1]["rate"],f'i{i}')
        solver.Add(demands[i-1]["rate"] * var_lambda - real_variables[f'i{i}']  <=0)
    #Creating real and binary flow variables
    for i in range(1,len(demands)+1):
        for router in routers:
            for link in links:
                if router in link[0]:
                        real_variables[f'ri{i}_{link[1]}{link[0]}']= solver.NumVar(0, solver.infinity(),f'ri{i}_{link[1]}{link[0]}')
                        real_variables[f'ri{i}_{link[0]}{link[1]}']= solver.NumVar(0, solver.infinity(),f'ri{i}_{link[0]}{link[1]}')
                        bin_variables[f'i{i}_{link[1]}{link[0]}']= solver.IntVar(0,1,f'i{i}_{link[1]}{link[0]}')
                        bin_variables[f'i{i}_{link[0]}{link[1]}']= solver.IntVar(0,1,f'i{i}_{link[0]}{link[1]}')
    #Creating real flow constraint
    pos_var=[]
    neg_var=[]
    for i in range(1,len(demands)+1):
        for router in routers:
            for link in links:
                if router == link[0]:
                    pos_var.append(real_variables[f'ri{i}_{link[1]}{link[0]}'])
                    neg_var.append(real_variables[f'ri{i}_{link[0]}{link[1]}'])
                elif router == link[1]:
                    pos_var.append(real_variables[f'ri{i}_{link[0]}{link[1]}'])
                    neg_var.append(real_variables[f'ri{i}_{link[1]}{link[0]}'])
            for values in subnets.values():
                if(router in values["routers"] and demands[i-1]['src'] in values["hosts"]):
                    pos_var.append(real_variables[f'i{i}'])
                elif(router in values["routers"] and demands[i-1]['dst'] in values["hosts"]):
                    neg_var.append(real_variables[f'i{i}'])
            solver.Add(solver.Sum(pos_var)- solver.Sum(neg_var)==0)
            pos_var.clear()
            neg_var.clear()
    #Creating binary flow constraint(unsplittable flow)
    pos_var=[]
    neg_var=[]
    for i in range(1,len(demands)+1):
        for router in routers:
            for link in links:
                if router == link[0]:
                    pos_var.append(bin_variables[f'i{i}_{link[1]}{link[0]}'])
                    neg_var.append(bin_variables[f'i{i}_{link[0]}{link[1]}'])
                elif router == link[1]:
                    pos_var.append(bin_variables[f'i{i}_{link[0]}{link[1]}'])
                    neg_var.append(bin_variables[f'i{i}_{link[1]}{link[0]}'])
            temp=True
            for values in subnets.values():
                if(router in values["routers"] and demands[i-1]['src'] in values["hosts"]):
                    solver.Add(solver.Sum(pos_var)- solver.Sum(neg_var)==-1)
                    temp=False
                elif(router in values["routers"] and demands[i-1]['dst'] in values["hosts"]):
                    solver.Add(solver.Sum(pos_var)- solver.Sum(neg_var)==1)
                    temp=False
            if(temp):
                solver.Add(solver.Sum(pos_var)- solver.Sum(neg_var)==0)
            pos_var.clear()
            neg_var.clear()   
    #Mutual exclusion for incoming in the same node
    pos_var.clear()
    for i in range(1,len(demands)+1):
        for router in routers:
            for link in links:
                if router == link[1]:
                    pos_var.append(bin_variables[f'i{i}_{link[0]}{link[1]}'])     
                elif router == link[0]:
                    pos_var.append(bin_variables[f'i{i}_{link[1]}{link[0]}'])
            if(len(pos_var)>0):
                solver.Add(solver.Sum(pos_var)<=1)
            pos_var.clear()
    #Mutual exclusion for outgoing from the same node 
    pos_var.clear()
    for i in range(1,len(demands)+1):
        for router in routers:
            for link in links:
                if router == link[0]:
                    pos_var.append(bin_variables[f'i{i}_{link[0]}{link[1]}'])    
                elif router == link[1]:
                    pos_var.append(bin_variables[f'i{i}_{link[1]}{link[0]}'])
            if(len(pos_var)>0):
                solver.Add(solver.Sum(pos_var)<=1)
            pos_var.clear()
    #Total flow link capacity
    pos_var.clear()
    for link,cost in links.items():
        for i in range(1,len(demands)+1):
            pos_var.append(real_variables[f'ri{i}_{link[0]}{link[1]}'])
            pos_var.append(real_variables[f'ri{i}_{link[1]}{link[0]}'])
        solver.Add(solver.Sum(pos_var)<=cost)
        pos_var.clear()
    #Flow capacity for each individual real variable
    for i in range(1,len(demands)+1):
        for link, cost in links.items():
            solver.Add(real_variables[f'ri{i}_{link[0]}{link[1]}']- cost*bin_variables[f'i{i}_{link[0]}{link[1]}'] <= 0)
            solver.Add(real_variables[f'ri{i}_{link[1]}{link[0]}']- cost* bin_variables[f'i{i}_{link[1]}{link[0]}']<= 0)
    # === Objective: maximize lambda ===
    solver.Maximize(var_lambda)
    # === Solve ===
    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL:
        if(outputModel):
            result={}
            for var in bin_variables:
                result[f'{var}']=bin_variables[var].solution_value()
            return result
        for i in range(1,len(demands)+1):
            print(f' The best goodput for flow demand #{i} is {round(real_variables[f'i{i}'].solution_value(),3)} Mbps')
    elif status == pywraplp.Solver.FEASIBLE:
        print("Feasible solution found, but not necessarily optimal.")
    elif status == pywraplp.Solver.INFEASIBLE:
        print("No feasible solution exists.")
    elif status == pywraplp.Solver.UNBOUNDED:
        print("The problem is unbounded.")
    else:
        print("Solver ended with status code:", status)

#=========================================================================================================================
class Topology(Topo):
    def build(self, **params):
        global routers, mininet_routers, hosts, mininet_hosts, subnets
        yamlFileName = params['yaml']

        with open(yamlFileName) as f:
                data = yaml.safe_load(f)
      
        # Get routers and add them to Mininet
        
        for router_name, interfaces in data.get("routers", {}).items():
            routers[router_name] = {}
            router = self.addHost(router_name, cls=LinuxRouter)
            mininet_routers[router_name]=router 
            for iface, config in interfaces.items():
                routers[router_name][iface] = {
                    "address": config["address"],
                    "mask": config["mask"],
                    "cost": config.get("cost", 1)
                }

        # Get hosts and add them to Mininet
        for host_name, interfaces in data.get("hosts",{}).items():
            hosts[host_name]={}
            host=self.addHost(host_name)
            mininet_hosts[host_name]=host
            for iface, config in interfaces.items():
                hosts[host_name][iface] = {
                    "address": config["address"],
                    "mask": config["mask"],
                    "subnet": get_subnet(config["address"],config["mask"])
                }


        #Create subnets dictionary
        for router,interfaces in routers.items():
            for interface,config in interfaces.items():
                subnet= get_subnet(config["address"],config["mask"])
                if(subnet not in subnets):
                    subnets[subnet]={}
                    subnets[subnet]["routers-interface"]=[[router,interface]]
                    subnets[subnet]["cost"]=config["cost"]
                    subnets[subnet]["host-interface"]=[]
                    subnets[subnet]["routers"]=[router]
                    subnets[subnet]["hosts"]=[]
                else:
                    subnets[subnet]["routers-interface"].append([router,interface])
        for host, interfaces in hosts.items():
            for interface, config in interfaces.items():
                subnet= get_subnet(config["address"],config["mask"])
                subnets[subnet]["host-interface"].append([host, interface])
        #Create switches for subnets with netmask<=29
        switches={}
        mininet_switches={}
        for subnet in subnets: 
            if len(subnet)<=29:
                name="s"+str(len(switches)+1)
                switch = self.addSwitch(name)
                mininet_switches[name]=switch
                subnets[subnet]["switch"]=name
                switches[name]={}
                switches[name]["subnet"]=subnet
                switches[name]["routers-interface"]=subnets[subnet]["routers-interface"]
                switches[name]["host-interface"]=subnets[subnet]["host-interface"]

        #Create links
        for subnet in subnets.values():
            #Connect subnets with switches
            if "switch" in subnet: 
                #Connect routers to switch
                switch_name=subnet["switch"]
                for i in range(len(subnet["routers-interface"])):
                    router_name=subnet["routers-interface"][i][0]
                    interface_name=subnet["routers-interface"][i][1]
                    router_ip=routers[router_name][interface_name]["address"]
                    router_netmask=ip_to_bits(routers[router_name][interface_name]["mask"]).count('1')
                    self.addLink(mininet_switches[switch_name],mininet_routers[router_name], intfName1= f'{switch_name}-eth{i}', intfName2= f'{router_name}-{interface_name}', param2={'ip':f'{router_ip}/{router_netmask}' })
                #Connect host to switch
                for i in range(len(subnet["host-interface"])):
                    host_name=subnet["host-interface"][i][0]
                    interface_name=subnet["host-interface"][i][1]
                    host_ip=hosts[host_name][interface_name]["address"]
                    host_netmask=ip_to_bits(hosts[host_name][interface_name]["mask"]).count('1')
                    self.addLink(mininet_hosts[host_name],mininet_switches[switch_name], intfName1= f'{host_name}-{interface_name}', param1={'ip':f'{host_ip}/{host_netmask}'} )
            #Connect subnets without switches
            else:
                if len(subnet["routers-interface"])==2:
                    first_router_name=subnet["routers-interface"][0][0]
                    first_interface_name=subnet["routers-interface"][0][1]
                    second_router_name=subnet["routers-interface"][1][0]
                    second_interface_name=subnet["routers-interface"][1][1]
                    self.addLink(mininet_routers[first_router_name], mininet_routers[second_router_name],
                                intfName1= f'{first_router_name}-{first_interface_name}', intfName2= f'{second_router_name}-{second_interface_name}')
                else: 
                    router_name=subnet["routers-interface"][0][0]
                    router_interface_name=subnet["routers-interface"][0][1]
                    host_name=subnet["host-interface"][0][0]
                    host_interface_name=subnet["host-interface"][0][1]
                    self.addLink(mininet_routers[router_name], mininet_hosts[host_name],
                                intfName1= f'{router_name}-{router_interface_name}', intfName2= f'{host_name}-{host_interface_name}')
    




def main():
    global routers, mininet_routers, hosts, mininet_hosts, subnets, demands

#HELP FUNCTION
    if len(sys.argv)==2 and sys.argv[1] in ('-h', '--help'):
        print_help()
#PRINT CPLEX LP FUNCTION
    elif len(sys.argv)==3 and sys.argv[1] in ('-l', '--lp'):
        yamlFileName = sys.argv[2]
        print_problem(yamlFileName)
#SOLVE LP PROBLEM FUNCTION
    elif len(sys.argv)==3 and sys.argv[1] in ('-p','--print'):
        yamlFileName=sys.argv[2]
        solve_problem(yamlFileName, False)
#START THE MININET EMULATOR
    elif len(sys.argv)==2:
        yamlFileName = sys.argv[1]
        t = Topology(yaml=yamlFileName)
        net = Mininet(topo=t, link=TCLink)
        net.start()


        #Create host interfaces
        for host,interfaces in hosts.items():
            for interface,config in interfaces.items():
                net[host].cmd(f'ifconfig {host}-{interface} {config["address"]} netmask {config["mask"]}')
                net[host].cmd(f'ifconfig {host}-{interface} up')
        #Create router interfaces
        for router,interfaces in routers.items():
            for interface,config in interfaces.items():
                net[router].cmd(f'ifconfig {router}-{interface} {config["address"]} netmask {config["mask"]}')
                net[router].cmd(f'ifconfig {router}-{interface} up')
        #Set default routes for hosts
        for value in subnets.values():
            for item in value["host-interface"]:
                host_name= item[0]
                host_interface=item[1]
                router_address= routers[value["routers-interface"][0][0]][value["routers-interface"][0][1]]["address"]
                net[host_name].cmd(f'ip route add default via {router_address} dev {host_name}-{host_interface}')
        
        #Find cheapest path for routers and Add cheapest path to router ip routes
        #This is the same code from the previous assignment, I have decided to keep it just to allow the network to work correctly even for not pre-defined "demands"
        #The ack messages will follow these paths, that might vary form the one from the best solution, however I'll follow the assumption that ACK size is negligible  
        router_connection={}
        for router,interfaces in routers.items():
                router_connection[router]={}
                router_connection[router]["subnets"]=[]
                router_connection[router]["connections"]=[]
                for interface,config in interfaces.items():
                    subnet= get_subnet(config["address"],config["mask"])
                    router_connection[router]["subnets"].append(subnet)
                    for values in subnets[subnet]["routers-interface"]:
                        if values[0]!=router:
                            router_connection[router]["connections"].append([values[0],routers[values[0]][values[1]]["address"], subnets[subnet]["cost"]])
        for router in routers:
            for subnet in subnets:        
                best_route=calculate_path(router,subnet, router_connection)
                if(best_route!=router):
                    mask_size=len(subnet)
                    decimal_subnet=transform_binary_string(subnet)
                    net[router].cmd(f'ip route add {decimal_subnet}/{mask_size} via {best_route}')
                    print(best_route)

        #Get the result of the linear programming model
        routers.clear()
        hosts.clear()
        subnets.clear()
        demands.clear()
        bin_variables=solve_problem(yamlFileName, True)
        #Enable MPLS forwarding on all routers
        for router, iface in routers.items():
            for interface in iface:
                net[router].cmd(f'echo 1 > /proc/sys/net/mpls/conf/{router}-{interface}/input')
        for i in range(0,len(demands)):
            for value in hosts[demands[i]["dst"]].values():
                destination_ip=value["address"]
            #find first and lastrouter encapsulates the message 
            for subnet in subnets.values():
                if demands[i]["src"] in subnet["hosts"]:
                    first_router=subnet["routers"][0]
                    second_router=first_router
                if demands[i]["dst"] in subnet["hosts"]:
                    last_router=subnet["routers-interface"][0][0]
                    last_router_interface=subnet["routers-interface"][0][1]
            is_first_router=True
            while(second_router!=last_router):
            #Find the second routers
                found=False
                for subnet in subnets.values():
                    if first_router in subnet["routers"]:
                        for second_router in subnet["routers"]:
                            if second_router!=first_router:
                                if bin_variables[f'i{i+1}_{first_router}{second_router}'] ==1.0:
                                    #Get first interface and second router ip 
                                    for value in subnet["routers-interface"]:
                                        if first_router==value[0]:
                                            first_router_interface=value[1]
                                        if second_router==value[0]:
                                            second_router_interface=value[1]
                                            second_router_ip=routers[second_router][second_router_interface]["address"]
                                    found=True
                                    break
                                    
                    if(found):
                        break
                if(is_first_router):
                    net[first_router].cmd(f'ip route add {destination_ip}/32 encap mpls {100+i} via {second_router_ip} dev {first_router}-{first_router_interface}')
                    is_first_router=False
                else:
                    net[first_router].cmd(f'ip -f mpls route add {100+i} as {100+i} via inet {second_router_ip} dev {first_router}-{first_router_interface}')
                first_router=second_router
            net[last_router].cmd(f'ip -f mpls route add {100+i} via inet {destination_ip} dev {last_router}-{last_router_interface}')
            
        CLI(net)
        net.stop()

        

        
            





if __name__ == '__main__':
    main()