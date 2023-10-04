from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import OVSSwitch, Host,Node, OVSKernelSwitch, Controller, RemoteController, DefaultController
from mininet.cli import CLI
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info

class setUp(Topo):
	def __init__(self, **opts):
		Topo.__init__(self,**opts)

		h1= self.addHost('h1')
		h2= self.addHost('h2')
		h3= self.addHost('h3')
		h4 = self.addHost('h4')
		ser = self.addHost('Server1')
		ser2 = self.addHost('Server2')
		
		s1 = self.addSwitch('s1')
		s2 = self.addSwitch('s2')
		s3 = self.addSwitch('s3')
		s4 = self.addSwitch('s4')		

		self.addLink(h1,s1)
		self.addLink(h2,s2)	

		self.addLink(h3,s2)
		self.addLink(h4,s2)
		self.addLink(s1,s2,bw=200,delay='10ms')
		self.addLink(s1,s3,bw=500,delay='10ms')
		self.addLink(s2,s4,bw=500,delay='10ms')		

		self.addLink(ser,s3,bw=1000)
		self.addLink(ser2,s4,bw=1000)
		self.addLink(ser,s4,bw=1000)
		self.addLink(ser2,s3,bw=1000)
		






if __name__ == '__main__':
	opo = setUp()
	net = Mininet(topo=opo, link=TCLink,switch=OVSKernelSwitch,controller=DefaultController,autoSetMacs=True)
	setLogLevel('info')
	net.start()
	dumpNodeConnections(net.hosts)

	#server for https
	ser = net.get("Server1")
	ser.cmd("python -m SimpleHTTServer 80 &")

	#server for tftp
	se2 = net.get("Server2")
	se2.cmd("/usr/sbin/in.tftpd -L -s /tftpboot &")

	#preventing broadcast
	for l in net.links:
		l.intf1.config(limit=2)

	#preventing https in hosts
	fw_rule1 = "iptables -A INPUT -p tcp --destination-port 80 ! -s {}"
	
	#preventing tftp
	fw_rule2 = "iptables -A -p INPUT -p udp --destination-port 69 ! -s {}"

	https1 = net.get('h1').IP()
	https2 = net.get('h2').IP()

	files = net.get('h3').IP()
	files2 = net.get('h4').IP()

	net.get('Server1').cmd(fw_rule2)
	net.get('Server2').cmd(fw_rule1)

	
	net.pingAll()
	CLI(net)
	net.stop()
