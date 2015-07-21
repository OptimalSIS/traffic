import random
import subprocess, os
import pickle
import time



start_time = time.time()
f_start = "<nodes>"
f_end = "</nodes>"
g_start = "<edges>"
g_end = "</edges>"
h_start = "<routes>"
h_end = "</routes>"
j_start = "<additional>"
j_end = "</additional>"


costF= {};         #the cost function
speed = 50         #speed of the cars
acc = 3            #acceleration of the car
decel = 3          #decceleration of the car
max_Car = 4        #max cars per 100 meters
#offset = random.randint(0, 93)    #the traffic light has a 94 second period
distUpper = 1000
distLower = 500      


#writing the edge file
def writeEdgeFile():
    g = open('cost.edg.xml', 'w')
    g.write(g_start)
    g.write('\n')
    thisline = '    <edge from="1" id="1to2" to="2" />'
    g.write(thisline)
    g.write('\n')
    thisline = '    <edge from="2" id="2to3" to="3" />'
    g.write(thisline)
    g.write('\n')
    g.write(g_end)
    g.close()



# writing the node file
def writeNodeFile(distance):
    f = open('cost.nod.xml', 'w')
    f.write(f_start)
    f.write("\n")
    # the lower left point is the origin
    thisline = '    <node id="1"  x="0.0" y="0.0" />'
    f.write(thisline)
    f.write('\n')
    thisline = '    <node id="2" type="traffic_light" ' + ' x="' + str(distance) + '"'
    thisline += ' y="0.0"' + '/>'
    f.write(thisline)
    f.write('\n')
    thisline = '    <node id="3"' + ' x="' + str(dist+20) + '"'
    thisline += ' y="0.0"' + '/>'
    f.write(thisline)
    f.write('\n')
    f.write(f_end)
    f.close()

#writing the route file
def writeRouFile(Car_Num):
    h = open('cost.rou.xml', 'w')
    h.write(h_start)
    h.write('\n')
    #car type, all cars are of the same type 
    thisline = '    <vType accel="' + str(acc) + '" decel="' + str(decel) + '" id="CarA" length="5.0" minGap="2.5" maxSpeed="'
    thisline += str(speed) + '"  sigma="0.5" />'
    h.write(thisline)
    h.write('\n')
    thisline = '    <route id="route0" edges="1to2 2to3"/>'
    h.write(thisline)
    h.write('\n')
    #cars to creat traffic 
    for m in range(0, Car_Num):
        thisline = '    <vehicle depart="0" departSpeed = "max" departPos = "'
        thisline += str(25*(Car_Num-m)) + '" id="'
        thisline += str(m) + '" ' + 'route="route0"' + ' type="CarA" />'
        h.write(thisline)
        h.write('\n') 
    #the car for the timing
    thisline = '    <vehicle depart="0" departSpeed = "max" id="new" route="route0" type="CarA" color="1,0,0" />'
    h.write(thisline)
    h.write('\n')
    h.write(h_end)
    h.close()


#writing the additional file regarding the traffic light
def writeAddFile(offsetTime):
    j = open('cost.add.xml', 'w')
    j.write(j_start)
    j.write('\n')
    thisline ='    <tlLogic id="2" programID="my_program" offset="' + str(offsetTime) + '" type="static">'
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
    j.write(j_end)
    j.close()


#read the output file and parse the info
def readOutput():
    tt = open('cost.output.xml', 'r')
    finishTime = {}   #records the finish time for all vehicles, key is vehicle name, value is finish time
    for line in tt:
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
            if(curVeh == 'new' and curEdge == '2to3'):
                break
    tt.close()
    return curTime





writeEdgeFile()


for offset in range(0, 94):
    writeAddFile(offset)
    for dist in range(distLower, distUpper+1, 100):
        writeNodeFile(dist)
        total_Car = max_Car*int(dist/100);
        for n_car in range(0, total_Car+1):
            writeRouFile(n_car)
            # call the command line to generate the maze.net.xml file
            subprocess.call(['netconvert64', '-c', 'cost.netc.cfg'], shell=True)
            # call the command line to run sumo
            subprocess.call(['sumo64', '-a', 'cost.add.xml', '-c', 'cost.sumo.cfg'], shell=True)
            curTime = readOutput()
            costF[str((dist, offset, n_car))] = curTime;





#print('Total cars: ' + str(n_car) + '\n')
#print('Total distance: ' + str(dist) + '\n')
#print('Offset: ' + str(offset) + '\n')
#print('Time spent: ' + str(curTime) + '\n')


with open('costF.pickle', 'wb') as saveData:
    pickle.dump(costF, saveData)

with open('costF.pickle', 'rb') as restoreData:
    ccc = pickle.load(restoreData)


print(costF); 
print(ccc);

print("--- %s seconds ---" % (time.time() - start_time))


