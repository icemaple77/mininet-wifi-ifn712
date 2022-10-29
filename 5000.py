#!/usr/bin/python
import sys
import random
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.cli import CLI
from randmac import RandMac
from mininet.node import OVSKernelSwitch

#version = 2

# set the number of access points in one layer
aps_singleLayer = 4

# set the number of stations in one ap
stations_singleAp = 50

# set the number of stations
total_stations = 5000

# set the inital x of site
x = 850

# set the inital y of site
y = 850

# set the initial z of site
z= -10

# set the high of one layer
h= 10

# set the crossing distance between signals
c= 450

def topology():
    global x,y,z
    # set the number of access points
    total_aps = int(total_stations/stations_singleAp)

    # set the number of switches
    total_switches = int(total_aps/aps_singleLayer)

    # the mac of station
    mac_station = set()

    # the mac of ap
    mac_ap = set()

    # the ip of station
    ip_station = set()

    # the ip of ap
    ip_ap = set()

    # set access points
    aps = []
    for ap in range(total_aps):
        aps.append('ap%s' % (ap))

    # set stations
    stas = []
    for sta in range(total_stations):
        stas.append('sta%s' % (sta))

    # set switches
    switches = []
    for switch in range(total_switches):
        switches.append('s%s' % (switch))

    # for access points
    fillIP(ip_ap,total_aps)
    fillMac(mac_ap,total_aps)

    # for stations
    fillIP(ip_station,total_stations)
    fillMac(mac_station,total_stations)

    info("*** Create network\n\n")
    # method for auto selecting the ap with strongest signal
    ac_method = 'ssf'
    if '-llf' in sys.argv:
        ac_method = 'llf'

    net = Mininet_wifi(ac_method=ac_method)

    info( '*** Adding controller\n' )
    c0 = net.addController('c0')
    
    # initialize index
    index_ap = 0
    index_sta = 0
    index_switch = 0
    layer = 1 

    for sta in stas:
        if(index_sta % stations_singleAp == 0):
            if(index_ap % aps_singleLayer == 0):
                info( '\n*** Add Switch\n')
                globals()[switches[index_switch]] = net.addSwitch(switches[index_switch], cls=OVSKernelSwitch)
                print(("%s Added at Layer %s")%(switches[index_switch],str(layer)))
                index_switch = index_switch + 1
                layer = layer + 1 
            info( '\n*** Add AP\n')
            setApPosition(index_ap)
            position = ('%s,%s,%s' %(x,y,z))
            channel = ('%s'%random.randint(1,10))
            globals()[aps[index_ap]] = net.addAccessPoint(aps[index_ap], ssid='ssid-' + aps[index_ap],channel = channel, mode='g', position=position, mac=list(mac_ap)[index_ap],ip=list(ip_ap)[index_ap])
            print(("%s at (%s)"%(aps[index_ap],position)) + " Channel:" + channel)
            index_ap = index_ap + 1
            info( '\n*** Add stations\n')
        host_position = ('%s,%s,%s' % (x+random.randint(-150,150),y+random.randint(-150,150),z))
        globals()[sta] = net.addStation(sta,position=host_position, mac=list(mac_station)[index_sta],ip=list(ip_station)[index_sta])
        index_sta = index_sta + 1 
        info(sta + " ")
    info("\n")

    info("\n*** Configuring Propagation Model\n\n")
    net.setPropagationModel(model="logDistance", exp=3)

    info("*** Configuring wifi nodes\n\n")
    net.configureWifiNodes()

    info( '*** Add links\n')
    index_switch = -1
    for index in range(0,total_switches-1):
        net.addLink(switches[index],switches[index+1])
        info("(%s,%s)"%(switches[index],switches[index+1])+ " ")
    for index in range(0,total_aps):
        if(index % aps_singleLayer == 0):
            index_switch = index_switch + 1
        net.addLink(switches[index_switch],aps[index])
        info("(%s,%s)"%(switches[index_switch],aps[index])+ " ")
        
    # net.plotGraph(max_x=1500, max_y=1500)

    info( '\n\n*** Starting network\n\n')
    net.build()

    info( '*** Starting controllers\n\n')
    c0.start()

    info( '*** Starting Switches/APs\n')
    for swtich in switches:
        net.get(swtich).start([c0])
        info(("%s ")%(swtich))
    for ap in aps:
        net.get(ap).start([c0])
        info(("%s ")%(ap))
    
    info("\n\n*** Running CLI\n\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()

def fillMac(_set,num):
    while(len(_set)<=num):
        _set.add(str(RandMac()))

def fillIP(_set,num):
    while(len(_set)<=num):
        _set.add(randomIP())

def randomIP():
    part_IP = ['%s'%random.randint(0, 255) for i in range(3)]
    part_IP.insert(0,'10')
    return '.'.join(part_IP)+'/8'

def setApPosition(index):
    global x,y,z
    index=index%aps_singleLayer
    if (index==0):
        z = z + h
        x = x - c
        y = y - c
    if (index==1): 
        z = z
        x = x + c
        y = y
    if(index==2):
        z = z
        x = x - c
        y = y + c
    if(index==3):
        z = z
        x = x + c
        y = y
    return x,y,z

if __name__ == '__main__':
    setLogLevel( 'info' )
    topology()

