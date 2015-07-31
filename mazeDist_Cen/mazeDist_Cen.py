#in this method, we first compute the optimal route for each affected vehicle in a distributed fashion
#then we recompute the optimal route for each affected car one by one centralizedly
import random
import subprocess, os
import pickle
import itertools
import math
import time
import copy
import collections

#load the dictionary for the cost function
with open('costF.pickle', 'rb') as restoreData:
    costF = pickle.load(restoreData)

######################################################################
#parameters
######################################################################
grid = 4   # we are going to create a grid by grid square
gridsize = 10**2
n_route = 4   # number of different routes for each of the four start-to-end trips, each route can have multiple cars
n_car = 10
randSeed = 1
crushTime = 100
badRoad1 = "21to22"
badRoad2 = "22to21"

speed = 50         #speed of the cars
acc = 3            #acceleration of the car
decel = 3          #decceleration of the car
max_Car = 4        #max cars per 100 meters

f_start = "<nodes>"
f_end = "</nodes>"
g_start = "<edges>"
g_end = "</edges>"
h_start = "<routes>"
h_end = "</routes>"

######################################################################
#Functions
######################################################################
### writing the node file
def writeNodeFile(filename, xgrid, ygrid):
    f = open(filename, 'w')
    f.write(f_start)
    f.write("\n")
    # the lower left point is the origin
    thisline = '    <node id="00" x="0.0" y="0.0" />'
    f.write(thisline)
    f.write('\n')
    #create the grid
    for i in range(1,grid):
        thisline = '    <node id="' + str(i) + str(0) + '"' + ' type="traffic_light" x="' + str(xgrid[i-1]) + '"'
        thisline += ' y="0.0"' + '/>'
        f.write(thisline)
        f.write('\n')
    thisline = '    <node id="' + str(grid) + str(0) + '"' + ' x="' + str(xgrid[grid-1]) + '"'
    thisline += ' y="0.0"' + '/>'
    f.write(thisline)
    f.write('\n')
    for j in range(1,grid):
        thisline = '    <node id="' + str(0) + str(j) + '"' + ' type="traffic_light" x="0.0"' 
        thisline += ' y="' + str(ygrid[j-1]) + '"' + '/>'
        f.write(thisline)
        f.write('\n')
    thisline = '    <node id="' + str(0) + str(grid) + '"' + ' x="0.0"' 
    thisline += ' y="' + str(ygrid[grid-1]) + '"' + '/>'
    f.write(thisline)
    f.write('\n')
    for i in range(1,grid+1):
        for j in range(1,grid+1):
            if(i==grid and j==grid):
                thisline = '    <node id="' + str(grid) + str(grid) + '"' + ' x="' + str(xgrid[grid-1]) + '"'
                thisline += ' y="' + str(ygrid[grid-1]) + '"' '/>'
                f.write(thisline)
                f.write('\n')
            else:
                thisline = '    <node id="' + str(i) + str(j) + '"' + ' type="traffic_light"  x="' + str(xgrid[i-1]) + '"'
                thisline += ' y="' + str(ygrid[j-1]) + '"' '/>'
                f.write(thisline)
                f.write('\n')
    f.write(f_end)
    f.close()

###writing the edge file
def writeEdgeFile(filename, num_of_grids):
    g = open(filename, 'w')
    g.write(g_start)
    g.write('\n')
    #connecting adjacent nods
    for i in range(0, num_of_grids+1):
        for j in range(0, num_of_grids+1):
            if(i<grid):
                rightline = '    <edge from="' + str(i)+str(j) + '"'
                rightline += ' id="' + str(i) + str(j) + 'to' + str(i+1) + str(j) + '"'
                rightline += ' to="' + str(i+1) + str(j) + '"' + '/>'
                g.write(rightline)
                g.write('\n')
                rightlineback = '    <edge from="' + str(i+1)+str(j) + '"'
                rightlineback += ' id="' + str(i+1) + str(j) + 'to' + str(i) + str(j) + '"'
                rightlineback += ' to="' + str(i) + str(j) + '"' + '/>'
                g.write(rightlineback)
                g.write('\n')
            if(j<grid): 
                upline = '    <edge from="' + str(i)+str(j) + '"'
                upline += ' id="' + str(i) + str(j) + 'to' + str(i) + str(j+1) + '"'
                upline += ' to="' + str(i) + str(j+1) + '"' + '/>'
                g.write(upline)
                g.write('\n')
                uplineback = '    <edge from="' + str(i)+str(j+1) + '"'
                uplineback += ' id="' + str(i) + str(j+1) + 'to' + str(i) + str(j) + '"'
                uplineback += ' to="' + str(i) + str(j) + '"' + '/>'
                g.write(uplineback)
                g.write('\n')
    g.write(g_end)
    g.close()


###writing the additional file regarding the traffic light
def writeAddFile(filename, num_of_grids):
    j = open(filename, 'w')
    j.write('<additional>')
    j.write('\n')
    for ipos in range(0, num_of_grids+1):
        for jpos in range(0, num_of_grids+1):
            if([ipos,jpos] != [0,0] and [ipos,jpos] != [0, num_of_grids] and [ipos,jpos] != [num_of_grids, 0] and [ipos,jpos] != [num_of_grids,num_of_grids]):
                offsetTime = 0
                thisId = str(ipos) + str(jpos)    
                thisline ='    <tlLogic id="' + thisId + '" programID="my_program" offset="' + str(offsetTime) + '" type="static">'
                j.write(thisline)
                j.write('\n')
                thisline = '        <phase duration="31" state="GGggrrrrGGggrrrr"/>'
                j.write(thisline)
                j.write('\n')
                thisline = '        <phase duration="5" state="yyggrrrryyggrrrr"/>'
                j.write(thisline)
                j.write('\n')
                thisline = '        <phase duration="6" state="rrGGrrrrrrGGrrrr"/>'
                j.write(thisline)
                j.write('\n')
                thisline = '        <phase duration="5" state="rryyrrrrrryyrrrr"/>'
                j.write(thisline)
                j.write('\n')
                thisline = '        <phase duration="31" state="rrrrGGggrrrrGGgg"/>'
                j.write(thisline)
                j.write('\n')
                thisline = '        <phase duration="5" state="rrrryyggrrrryygg"/>'
                j.write(thisline)
                j.write('\n')
                thisline = '        <phase duration="6" state="rrrrrrGGrrrrrrGG"/>'
                j.write(thisline)
                j.write('\n')
                thisline = '        <phase duration="5" state="rrrrrryyrrrrrryy"/>'
                j.write(thisline)
                j.write('\n')
                j.write('    </tlLogic>')
                j.write('\n')
    j.write('</additional>')
    j.close()

###writing the route file
def writeRouFile(filename):
    vehRous = {}
    h = open(filename, 'w')
    h.write(h_start)
    h.write('\n')
    #car type
    thisline = '    <vType accel="' + str(acc) + '" decel="' + str(decel) + '" id="CarA" length="5.0" minGap="2.5" maxSpeed="'
    thisline += str(speed) + '"  sigma="0.5" />'
    h.write(thisline)
    h.write('\n')
    for i in range(0,len(trips)):
        if(i == 0):    #lowerleft_to_upperright
            x_movement = 1
            y_movement = 1
            x_start = 0
            y_start = 0
        if(i == 2):    #upperleft_to_lowerright
            x_movement = 1
            y_movement = -1
            x_start = 0
            y_start = grid
        if(i == 1):    #lowerright_to_upperleft
            x_movement = -1
            y_movement = 1
            x_start = grid
            y_start = 0
        if(i == 3):    #upperright_to_lowerleft
            x_movement = -1
            y_movement = -1
            x_start = grid
            y_start = grid
        #for each trip, generate n_route random routes
        for j in range(0, n_route):
            pos = list(range(0, grid*2))   #position to be shuffled
            random.seed(j)  
            random.shuffle(pos)
            finalpos = sorted(pos[0:grid]) #position of the x-movement  
            thisline = '    <route id="' + trip_names[i] + str(j) + '" edges="'
            thisRou = '' 
            x_pos_1 = x_start
            y_pos_1 = y_start
            #the exact route
            for k in range(0, grid*2):
                if(k in finalpos):
                    x_pos_2 = x_pos_1 + x_movement
                    y_pos_2 = y_pos_1
                else:
                    x_pos_2 = x_pos_1
                    y_pos_2 = y_pos_1 + y_movement
                thisRou += str(x_pos_1) + str(y_pos_1) + 'to' + str(x_pos_2) + str(y_pos_2) + ' '
                x_pos_1 = x_pos_2
                y_pos_1 = y_pos_2 
            thisRou = thisRou[0:-1]   #remove the last space
            thisline += thisRou
            thisline += '"/>'
            h.write(thisline)
            h.write('\n')
            for m in range(0, n_car):
                thisline = '    <vehicle depart="0" id="'
                vehId = trip_names[i] + str(j) + 'veh' + str(m)
                vehRous[vehId] = thisRou
                thisline += vehId + '" '
                thisline += 'route="' + trip_names[i] + str(j) + '" type="CarA" />'
                h.write(thisline)
                h.write('\n') 
    h.write(h_end)
    h.close()
    return vehRous

###generate the starting and ending location for the new car
def newPosition(grid):
    xpos = list(range(0, grid+1))
    random.seed(randSeed)
    random.shuffle(xpos)
    ypos = list(range(0, grid+1))
    random.seed(randSeed+2)
    random.shuffle(ypos)
    return (xpos[0], ypos[0]), (xpos[1], ypos[1]), xpos[1] - xpos[0], ypos[1] - ypos[0]


###generate all the possible routes for the new car. The idea is to generate all possible binary sequences 
###for given fixed number of zeros and ones. Then zeros correspond to the x-axis moves, ones correspond to the y-axis moves 
def allBinarySquence(zeros, ones):
    total = zeros + ones  #total number of digits
    S = list(range(0,total))
    tmp = list(itertools.combinations(S, zeros))
    res = []   #return a list of strings
    for elem in tmp:
        tmp = ""
        for pos in range(0,total):
            if(pos in elem):
                tmp = tmp + "0"
            else:
                tmp = tmp + "1"
        res.append(tmp)
    return res


###read data from the output file
def readFile(filename, unaffectedVeh):
    f = open(filename, 'r')
    finishTime = {}   #records the finish time for all vehicles, key is vehicle name, value is finish time
    vehNums = {}      #number of vehicles on a specific edge at a specific time
                  #key is a tuple with time and edge name, value is a number
    startTime = {}    #records the time for every car to be on the road
    crushEdge = {}  #records the car edges at the time of crush
    newTime = {}    #records the time when the cars arrive at a new node right after the crush
                    #this is the last time the car in the current edge where the crush happens
    vehNums_change = {}  #this records the impact of each unaffected veh on the vehNums after the crush
                        # key is the unaffected  veh, value is also a dict, with key being the time and value being the edge
    for line in f:
        linelist = line.split()
        if(len(linelist) > 1 and linelist[0] == '<timestep'):
            endPos = 6
            while(True):
                if(linelist[1][endPos] == '.'):
                    break
                else:
                    endPos += 1   
            curTime = int(linelist[1][6:endPos])
        elif(len(linelist) > 1 and linelist[0] == '<edge'):
            endPos = 4
            while(True):
                if(linelist[1][endPos] == '"'):
                    break
                else:
                    endPos += 1
            curEdge = linelist[1][4:endPos]
        elif(len(linelist) > 1 and linelist[0] == '<vehicle'):
            endPos = 4
            while(True):
                if(linelist[1][endPos] == '"'):
                    break
                else:
                    endPos += 1
            curVeh = linelist[1][4:endPos]
            #if the car is right at a cross, do something 
            if("_" in curEdge):
                curNode = curEdge.split('_')[0][1:]
                edgeList = vehRous[curVeh].split()
                for e in edgeList:
                    if(curNode == e[0:2]):
                        curEdge = e
                        break 
            #after the crush, only record the unaffected cars
            if(curTime >= crushTime and curVeh in unaffectedVeh):
                curKey = (curTime, curEdge)
                if(curKey in vehNums):
                    vehNums[curKey] += 1
                else:
                    vehNums[curKey] = 1
                #update the vehNums_change
                if(curVeh not in vehNums_change):
                    curMap = {}
                    vehNums_change[curVeh] = curMap
                curMap = vehNums_change[curVeh]
                curMap[curTime] = curEdge
            #remember the cars locations at the time of the crush
            if(curTime == crushTime):
                crushEdge[curVeh] = curEdge
                newTime[curVeh] = curTime
            #update
            if(curVeh in crushEdge and crushEdge[curVeh] == curEdge):
                newTime[curVeh] = curTime
            finishTime[curVeh] = curTime + 1
            if(curVeh not in startTime):
                startTime[curVeh] = curTime   
    f.close()
    return vehNums, finishTime, startTime, crushEdge, newTime, vehNums_change


###generate the route file with the new car
def writeNewRouFile(filename, newRoutes):
    newRoutes_Ordered = collections.OrderedDict(sorted(newRoutes.items(), key = lambda t:t[0]))
    h = open(filename, 'w')
    h.write(h_start)
    h.write('\n')
    #car type
    thisline = '    <vType accel="' + str(acc) + '" decel="' + str(decel) + '" id="CarA" length="5.0" minGap="2.5" maxSpeed="'
    thisline += str(speed) + '"  sigma="0.5" />'
    h.write(thisline)
    h.write('\n')
    addedRoute = []
    for veh in newRoutes_Ordered:
        thisRoute = newRoutes_Ordered[veh]
        if(thisRoute not in addedRoute):
            thisline = '    <route id="' + thisRoute + '" edges="' + thisRoute + '"/>'  
            addedRoute.append(thisRoute)
            h.write(thisline)
            h.write('\n')
        thisline = '    <vehicle depart="0" id="' + veh + '" '
        thisline += 'route="' + thisRoute + '" type="CarA" />'
        h.write(thisline)
        h.write('\n') 
    h.write(h_end)
    h.close()

###for any binary sequence, generate the corresponding route, update the vehNums along the route
###return the new route, a copy of the updated vehNums
###also return a copy of the change of the traffic, which is a map: time to edge
def route_and_vehNums(route_binary, vehNumss, cur_x, cur_y, cur_Time, edgeLen, x_step, y_step): 
    curNewRoute = ""
    vehNums_copy = copy.deepcopy(vehNumss)
    veh_change = {}
    for elem in route_binary:
        if(elem == '0'):
            next_x = cur_x + x_step
            next_y = cur_y
        else:
            next_x = cur_x
            next_y = cur_y + y_step
        curEdge = str(cur_x)+str(cur_y) + 'to' + str(next_x) + str(next_y)
        curNewRoute += curEdge + ' '
        curDist = edgeLen[curEdge]
        curKey = (cur_Time, curEdge) 
        curOffset = cur_Time%94
        if(curKey in vehNumss):
            curNum = vehNumss[curKey]
        else:
            curNum = 0
        if(curNum > curDist * max_Car/100):
            curNum = int(curDist * max_Car/100)
        timeSpent = costF[str((curDist, curOffset, curNum))]
        cur_x = next_x
        cur_y = next_y
        for timeSlot in range(0, timeSpent):
            modifyTime = cur_Time + timeSlot
            veh_change[modifyTime] = curEdge
            modifyKey = (modifyTime, curEdge)
            if(modifyKey in vehNums_copy):
                vehNums_copy[modifyKey] += 1
            else:
                vehNums_copy[modifyKey] = 1  
        cur_Time += timeSpent  
    return curNewRoute[:-1], vehNums_copy, cur_Time, veh_change


###generate the new route file with the new car and run the simulation with the new car
def run_new_simu(curNewRoute, new_car_start_time):
    ##writing the new route file
    writeNewRouFile('newmaze.rou.xml', 'maze.rou.xml', curNewRoute[0:-1], str(new_car_start_time))
    ## call the command line to run sumo with newcar
    subprocess.call(['sumo64', '-a', 'maze.add.xml', '-c', 'newmaze.sumo.cfg'], shell=True)



###given the new vehNums_copy, estimate all unaffected cars total time and the sum
###the total time is calculated from the time of the crush
def estOtherTotal(theseVeh, edgeLen, vehNums_copy, newTime, newRoutes):
    timeEst = {}   
    new_total_est = 0
    for everyV in theseVeh:
        nowTime = newTime[everyV]
        nowRoute = newRoutes[everyV]
        routeList = nowRoute.split()
        for edge in routeList:
            nowOffset = nowTime%94
            nowDist = edgeLen[edge]
            locations = edge.split("to")
            trafficLight = locations[1]
            nowKey = (nowTime, edge)
            if(nowKey in vehNums_copy):
                nowNum = vehNums_copy[nowKey]
            else:
                nowNum = 0
            nowNum = min(nowNum, int(nowDist/100*max_Car))
            timeCost = costF[str((nowDist, nowOffset, nowNum))]
            nowTime += timeCost
        timeEst[everyV] = nowTime
        new_total_est += timeEst[everyV]
    return new_total_est


###read data from the output file
def totalTime(filename):
    f = open(filename, 'r')
    finishTime = {}   #records the finish time for all vehicles, key is vehicle name, value is finish time
    for line in f:
        linelist = line.split()
        if(len(linelist) > 1 and linelist[0] == '<timestep'):
            endPos = 6
            while(True):
                if(linelist[1][endPos] == '.'):
                    break
                else:
                    endPos += 1   
            curTime = int(linelist[1][6:endPos])
        elif(len(linelist) > 1 and linelist[0] == '<edge'):
            endPos = 4
            while(True):
                if(linelist[1][endPos] == '"'):
                    break
                else:
                    endPos += 1
            curEdge = linelist[1][4:endPos]
        elif(len(linelist) > 1 and linelist[0] == '<vehicle'):
            endPos = 4
            while(True):
                if(linelist[1][endPos] == '"'):
                    break
                else:
                    endPos += 1
            curVeh = linelist[1][4:endPos]
            finishTime[curVeh] = curTime + 1
    f.close()
    timeSpent = 0
    for veh in finishTime:
        timeSpent += finishTime[veh]   
    return timeSpent

##given any veh, find its start location after the crush, then generate all 
##binary sequences representing its all possible routes 
def findRouteSeq(anyVeh):
    curEdge = crushEdge[anyVeh]
    newStart = curEdge.split("to")[-1]
    new_car_start_pos = [int(newStart[0]), int(newStart[1])]
    newEnd = vehRous[anyVeh].split()[-1].split("to")[-1]
    new_car_end_pos = [int(newEnd[0]), int(newEnd[1])]
    x_move = int(newEnd[0]) - int(newStart[0])
    y_move = int(newEnd[1]) - int(newStart[1])
    x_step = int(abs(x_move)/x_move)
    y_step = int(abs(y_move)/y_move)
    #generate all binary sequence, each corresponds to route for the new car 
    route_sequence = allBinarySquence(abs(x_move), abs(y_move))
    new_car_start_time = newTime[anyVeh]
    return new_car_start_pos, route_sequence, new_car_start_time, x_step, y_step


##computation base on the centralized method
def centralized_all(curRoutes, fixed_route_veh, change_route_veh, vehNums_change, vehNums_cur):
    for anyVeh in change_route_veh:
        #delete the change made by this veh for the chosen route, this info is in vehNums_change
        update_map = vehNums_change[anyVeh]
        for timeSlot in update_map:
            updateEdge = update_map[timeSlot]
            updateKey = (timeSlot, updateEdge)
            vehNums_cur[updateKey] -= 1       
        new_car_start_pos, route_sequence, new_car_start_time, x_step, y_step = findRouteSeq(anyVeh)
        #find the optimal route for this particular vehicle
        optimal_grandTotal_est_B = 10**6
        optimal_route_est_B = ""
        #we will update the vehNums according to the optimal routes, now keep a copy
        vehNums_B_tmp = {}      
        #for this vehicle, choose the best route
        for everyRoute in route_sequence:
            cur_x = new_car_start_pos[0]
            cur_y = new_car_start_pos[1]
            #we will update the traffic info after we choose the optimal route for the first affected car
            curNewRoute_B, vehNums_copy, cur_Time_B, veh_change_B = route_and_vehNums(everyRoute, 
                              vehNums_cur, cur_x, cur_y, new_car_start_time, edgeLen, x_step, y_step)
            if(badRoad1 in curNewRoute_B or badRoad2 in curNewRoute_B):
                continue  
            new_car_travel_time_est_B = cur_Time_B - new_car_start_time
            ##given the new vehNums, estimate all other cars total time
            new_total_est_B = estOtherTotal(fixed_route_veh, edgeLen, vehNums_copy, newTime, curRoutes)
            new_grandTotal_est_B = new_car_travel_time_est_B + new_total_est_B
            #update the optimal time if necessary (estimation)
            if(optimal_grandTotal_est_B > new_grandTotal_est_B):
                optimal_grandTotal_est_B = new_grandTotal_est_B
                optimal_route_est_B = curNewRoute_B
                vehNums_B_tmp = copy.deepcopy(vehNums_copy)
        #update the vehNums according to this optimal routes
        vehNums_cur = copy.deepcopy(vehNums_B_tmp)    
        #add this route to the new route, which will be used for other affected cars
        curRoutes[anyVeh] = optimal_route_est_B
        fixed_route_veh.append(anyVeh)




######################################################################
#Generate the grid points
######################################################################
x_grid = []
y_grid = []


#randomly generate the grid
random.seed(randSeed)
x_grid.append(random.randint(5,10)*gridsize)
random.seed(randSeed)
y_grid.append(random.randint(5,10)*gridsize)

for i in range(1, grid):
    random.seed(randSeed+i)
    x_grid.append(x_grid[-1] + random.randint(5,10)*gridsize)
    random.seed(randSeed-i)
    y_grid.append(y_grid[-1] + random.randint(5,10)*gridsize)



##generate the dictionary to store all the lenghts of the edges
edgeLen = {}
for i in range(0, grid+1):
    for j in range(0, grid+1):
        if(i<grid):
            if(i==0):
                dist_tmp = x_grid[0]
            else:
                dist_tmp = x_grid[i] - x_grid[i-1]
            edgeLen[str(i)+str(j) + 'to' + str(i+1) + str(j)] = dist_tmp
            edgeLen[str(i+1)+str(j) + 'to' + str(i) + str(j)] = dist_tmp
        if(j<grid): 
            if(j==0):
                dist_tmp = y_grid[0]
            else:
                dist_tmp = y_grid[j] - y_grid[j-1]
            edgeLen[str(i)+str(j) + 'to' + str(i) + str(j+1)] = dist_tmp
            edgeLen[str(i)+str(j+1) + 'to' + str(i) + str(j)] = dist_tmp


######################################################################
#trips, tripnames
######################################################################
trips = []
trip_names = []
veh_names = []
#four start-to-end trips, each has n_route many routes
trips.append('00TO'+ str(grid) + str(grid))             #lowerleft_to_upperright
trip_names.append("lowerleft_to_upperright")
trips.append(str(grid) + '0'+ 'TO' + '0' + str(grid))   #lowerright_to_upperleft
trip_names.append("lowerright_to_upperleft")
trips.append('0' + str(grid) + 'TO' + str(grid) + '0')  #upperleft_to_lowerright
trip_names.append("upperleft_to_lowerright")
trips.append(str(grid) + str(grid) + 'TO00')            #upperright_to_lowerleft
trip_names.append("upperright_to_lowerleft")


######################################################################
#Generate all the necessary files
######################################################################
# writing the nod file
writeNodeFile('maze.nod.xml', x_grid, y_grid)

#writing the edge file
writeEdgeFile('maze.edg.xml', grid)

#writing the additional file regarding the traffic lights
writeAddFile('maze.add.xml', grid)

#writing the route file, vehRous returns the routes for all the cars
vehRous_raw = writeRouFile('maze.rou.xml')

vehRous = collections.OrderedDict(sorted(vehRous_raw.items(), key = lambda t:t[0]))



#find the affected vehicles and unaffected vehicles
affectedVeh = []
unaffectedVeh = []

for veh in vehRous: 
    if(badRoad1 in vehRous[veh] or badRoad2 in vehRous[veh]):
        affectedVeh.append(veh)
    else:
        unaffectedVeh.append(veh)


######################################################################
#Run the simulation without the new car
######################################################################
# call the command line to generate the maze.net.xml file
subprocess.call(['netconvert64', '-c', 'maze.netc.cfg'], shell=True)

# call the command line to run sumo
subprocess.call(['sumo64', '-a', 'maze.add.xml', '-c', 'maze.sumo.cfg'], shell=True)


#read data from the output file
vehNums, finishTime , startTime, crushEdge, newTime, vehNums_change_unaffected = readFile('maze.output.xml', unaffectedVeh)



#record the new routes for the unaffected vehicles for later calculation
newRoutes = {}
for allVeh in unaffectedVeh:
    thisRoute = vehRous[allVeh]
    newRoutes[allVeh] = thisRoute.split(crushEdge[allVeh])[1][1:]

 


#compute the total time without the new car
old_total_simu = 0
for ve in finishTime:
    old_total_simu += finishTime[ve]

print("If no accident: ", old_total_simu, '#########')



######################################################################
#here we are going to recompute the routes for the affected cars one by one 
##A: after computing the new route for an affected car, we do not update the traffic info
##This is the computation done distributively
######################################################################
vehNums_A = copy.deepcopy(vehNums)
newRoutes_A = copy.deepcopy(newRoutes)
vehNums_change_A = {}

for anyVeh in affectedVeh:
    new_car_start_pos, route_sequence, new_car_start_time, x_step, y_step = findRouteSeq(anyVeh)
    #find the optimal route for this particular vehicle
    optimal_grandTotal_est_A = 10**6
    optimal_route_est_A = ""
    optimal_veh_change_A = {}
    #for this vehicle, choose the best route
    for everyRoute in route_sequence:
        cur_x = new_car_start_pos[0]
        cur_y = new_car_start_pos[1]
        #method A: we will not update the traffic info after we choose the optimal route for the first affected car
        curNewRoute_A, vehNums_copy_A, cur_Time_A, veh_change_A = route_and_vehNums(everyRoute, 
                  vehNums_A, cur_x, cur_y, new_car_start_time, edgeLen, x_step, y_step)
        if(badRoad1 in curNewRoute_A or badRoad2 in curNewRoute_A):
            continue         
        new_car_travel_time_est_A = cur_Time_A - new_car_start_time
        ##given the new vehNums, estimate all other cars total time
        new_total_est_A = estOtherTotal(unaffectedVeh, edgeLen, vehNums_copy_A, newTime, newRoutes)
        new_grandTotal_est_A = new_car_travel_time_est_A + new_total_est_A
        #update the optimal time if necessary (estimation)
        if(optimal_grandTotal_est_A > new_grandTotal_est_A):
            optimal_grandTotal_est_A = new_grandTotal_est_A
            optimal_route_est_A = curNewRoute_A
            optimal_veh_change_A = copy.deepcopy(veh_change_A) 
    #add this route to the new route
    newRoutes_A[anyVeh] = optimal_route_est_A
    vehNums_change_A[anyVeh] = optimal_veh_change_A
  


#update the routes after the distributive computation
for veh in affectedVeh:
    oldRoute = vehRous[veh]
    firstPart = oldRoute.split(crushEdge[veh])[0]
    newRoutes_A[veh] = firstPart + crushEdge[veh] + ' ' + newRoutes_A[veh]

for veh in unaffectedVeh:
    newRoutes_A[veh] = vehRous[veh]


#from final routes to write the files, not smartly coordinated
writeNewRouFile('newmazeA.rou.xml', newRoutes_A)
## call the command line to run sumo with newcar
subprocess.call(['sumo64', '-a', 'maze.add.xml', '-c', 'newmazeA.sumo.cfg'], shell=True)

timeSpent_A = totalTime('newmazeA.output.xml')

print("If accident and rerouted distributively, total time spent: ", timeSpent_A, '#########')



##after comupting the routes for the affected vehs distributively, we will once again 
##update the routes for the affected vehs in a centralized way.
##here after update each affected veh, we will use this data to update later affected vehs  
#here we do not need the newRoutes_A since we only need the difference of the traffic information
#which is stored in vehNums_change_A

vehNums_B = copy.deepcopy(vehNums)

#update the vehNums according to the vehNums_change_A
for Veh in vehNums_change_A:
    curMap = vehNums_change_A[Veh]
    for curTime in curMap:
        curEdge = curMap[curTime]
        curKey = (curTime, curEdge)
        if(curKey in vehNums_B):
            vehNums_B[curKey] += 1
        else:
            vehNums_B[curKey] = 1
           



newRoutes_B = copy.deepcopy(newRoutes)
unaffectedVeh_B = copy.deepcopy(unaffectedVeh)



centralized_all(newRoutes_B, unaffectedVeh_B, affectedVeh, vehNums_change_A, vehNums_B)

###### make a copy of the new routes for the future use, this part of the route is after the crush
##first copy the routes from newRoutes_B, here the affected cars have new routes, we will fix these in the following
newRoutes_C = copy.deepcopy(newRoutes_B)
######################

###add what happends before crush to have the full routes
for veh in affectedVeh:
    oldRoute = vehRous[veh]
    firstPart = oldRoute.split(crushEdge[veh])[0]
    newRoutes_B[veh] = firstPart + crushEdge[veh] + ' ' + newRoutes_B[veh]
   

for veh in unaffectedVeh:
    newRoutes_B[veh] = vehRous[veh]


#from final routes to write the files smartly coordinated
writeNewRouFile('newmazeB.rou.xml', newRoutes_B)
## call the command line to run sumo with newcar
subprocess.call(['sumo64', '-a', 'maze.add.xml', '-c', 'newmazeB.sumo.cfg'], shell=True)

timeSpent_B = totalTime('newmazeB.output.xml')

print("If accident and rerouted distributively then centralizedly for the affected vehicles, total time spent: ", timeSpent_B, '#########')


###########here we are going to reroute the unaffected cars 


affectedVeh_C = copy.deepcopy(affectedVeh)

centralized_all(newRoutes_C, affectedVeh_C, unaffectedVeh, vehNums_change_unaffected, vehNums_B)



for veh in affectedVeh:
    newRoutes_C[veh] = newRoutes_B[veh]
   

for veh in unaffectedVeh:
    oldRoute = vehRous[veh]
    firstPart = oldRoute.split(crushEdge[veh])[0]
    newRoutes_C[veh] = firstPart + crushEdge[veh] + ' ' + newRoutes_C[veh]

#from final routes to write the files
writeNewRouFile('newmazeC.rou.xml', newRoutes_C)
## call the command line to run sumo with newcar
subprocess.call(['sumo64', '-a', 'maze.add.xml', '-c', 'newmazeC.sumo.cfg'], shell=True)

timeSpent_C = totalTime('newmazeC.output.xml')

print("If accident and rerouted distributively then centralizedly for the affected vehicles and centralized for the unaffected vehicles, total time spent: ", timeSpent_C, '#########')


