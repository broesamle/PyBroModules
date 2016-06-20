#
#  WozualizeA.py
#  
#
#  Created by martinb on 6.02.2008.
#  Copyright (c) 2008 __MyCompanyName__. All rights reserved.
#

import  wx
import wx.lib.delayedresult as delayedresult

from WotilitiesA import identity, IterList, getSigmoid
from math import sin,cos,asin,acos,atan,atan2,tan,pi

##############################
### general Vizualizer for to use between the lines
### no full fledged interactive application but a nice tool to popup some window in betwen :-)
##############################

class Viz(object):
	""" Do not use in parallel with other applications or windows -- just for commandline based programs which need
		vizualization at specific points. 
		Show a vizualization windows which have to be built up before x.show() is called. 
		x.show() starts an application main loop!!!
		"""
	def __init__(self):
		self.app = wx.App()
		self.topframes = []
		

		# Create the menubar and a menu 
		menuBar = wx.MenuBar()
		menu = wx.Menu()

		# add an item to the menu, using \tKeyName automatically
		# creates an accelerator, the third param is some help text
		# that will show up in the statusbar
		menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit this simple sample")

		self.app.Bind(wx.EVT_MENU, self.OnTimeToClose, id=wx.ID_EXIT)
		
		self.nextX = 20
		self.nextY = 20
		self.maxHei = 0

	def OnTimeToClose(self, evt):
		"""Event handler for the button click."""
		print "Exiting ..."
		for f in self.topframes:
			f.Close()
			
	def showPic(self,filename,picformat=wx.BITMAP_TYPE_PNG):
		png = wx.Image(filename, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		wid,hei = (png.GetWidth(), png.GetHeight())

		if self.nextX + wid > 1024:		
			self.nextX = 20
			self.nextY = self.nextY + self.maxHei
			
		if self.nextY + hei > 1024:		
			self.nextX = 20
			self.nextY = 20
			
		frame = wx.MiniFrame( None, wx.ID_ANY, "Hello World", pos=(self.nextX,self.nextY), size=(wid,hei+10) )
		self.app.SetTopWindow(frame)
		self.topframes.append(frame)

		self.nextX = self.nextX + wid
		self.maxHei = max(self.maxHei,hei) 
		
		  

		wx.StaticBitmap(frame, -1, png, (0, 0), (wid,hei))

			
		frame.Show(True)
		
	def show(self):
		self.app.MainLoop()

def demoViz():
	v = Viz()
	v.showPic("g1.dot.png")
	v.showPic("g2.dot.png")
	v.show()

##############################
### Basic Applictions
##############################


class WApp(wx.App):
	""" An application which initializes one menu, an exit item as well as some administrative stuff like topframe lists.
		There are methods for to add menu items, topframes etc. The easiest way to create an application is to overload
		__init__ and put all your "personal" initialization in there and add further methods if necessary.
		then you simply have to start the event loop
		"""	
	
	def __init__(self):
		super(WApp,self).__init__(redirect=False)
		self.topframes = []
		self.menus = []
		self.menus.append(wx.Menu())		## at least one standard menu for to exit

		menuBar = wx.MenuBar()
		
		print (self.OnTimeToClose)
		self.addMenuItem("E&xit\tAlt-X",self.OnTimeToClose,id=wx.ID_EXIT)

	def addMenuItem(self, text, handler, id=wx.NewId(), help="Hilfetext fehlt :-)"):
		self.menus[0].Append(id,text,help)
		self.Bind(wx.EVT_MENU,handler,id=id)
		return id
		
	def addTopFrame(self,frame):
		self.topframes.append(frame)


	def OnTimeToClose(self, evt):
		"""Event handler for the button click."""
		print "Exiting ..."
		for f in self.topframes:
			f.Close()


##############################
### 2D Transformer
##############################

class Transformer2D(object):
	""" Transform (shift and scale) coordinates between different areas such that their proportions in relation 
		to the respective area is maintained."""
	def __init__(self,p1A,p2A,p1B,p2B):
		""" p1 is the upper left corner and p2 is the bottom right corner (for each of the two areas A and B)."""
		
		### XXminXX and XXmaxXX may have values such that XXminXX > XXmaxXX
		### this will happen if the axes of both coordinate systems run in different directions, e.g. one increases to the right
		### and the other one decreases to the right.
		self.xminA, self.yminA = p1A
		self.xmaxA, self.ymaxA = p2A
		self.xminB, self.yminB = p1B
		self.xmaxB, self.ymaxB = p2B

		### derived sizes
		self.widthA = self.xmaxA - self.xminA
		self.heightA = self.ymaxA - self.yminA
		self.widthB = self.xmaxB - self.xminB
		self.heightB = self.ymaxB - self.yminB

		if self.widthA != 0.0:		self.XfactorAB = float(self.widthB) / self.widthA
		else:						self.XfactorAB = 0.0
		
		if self.heightA != 0.0:		self.YfactorAB = float(self.heightB) / self.heightA 
		else:						self.YfactorAB = 0.0


		if self.widthB != 0.0:		self.XfactorBA = float(self.widthA) / self.widthB
		else:						self.XfactorBA = 0.0
		
		if self.heightB != 0.0:		self.YfactorBA = float(self.heightA) / self.heightB
		else:						self.YfactorBA = 0.0
	
	def xAB(self,x):
		return (x-self.xminA) * self.XfactorAB  +  self.xminB 

	def yAB(self,y):
		return (y-self.yminA) * self.YfactorAB  +  self.yminB 

	def xBA(self,x):
		return (x-self.xminB) * self.XfactorAB  +  self.xminA 

	def yBA(self,y):
		return (y-self.yminB) * self.YfactorBA  +  self.yminA 
	
	def pAB(self,p):
		""" transform a point p=(x,y)"""
		x,y = p
		return self.xAB(x), self.yAB(y)

	def pBA(self,p):
		""" transform a point p=(x,y)"""
		x,y = p
		return self.xBA(x), self.yBA(y)


	
##############################
### Color Maps
##############################

class Heatmap(object):
	def __init__(self,min=0.0,max=1.0,rgbMax=255):
		self.compress = lambda v:(v-min) / (max-min)
		self.rgbmax = rgbMax
		d = max - min
		m = (max+min) / 2.0
		
		self.rsigmo=getSigmoid(min+d*0.1,min+d*0.7)
		#self.rsigmo=lambda x : 0
		
		self.gsigmo=getSigmoid(min+d*0.5,min+d*1.1)
		#self.gsigmo=lambda x : 0

		self.bsigmo=getSigmoid(min+d*0.5,min-d*0.2)		## max < min?? this makes the sigmo decrease
	
	def r(self,v):
		return self.rgbmax * self.rsigmo(v) 
	
	def g(self,v):
		return self.rgbmax * self.gsigmo(v) 
	
	def b(self,v):
		return self.rgbmax * self.bsigmo(v) 
			
	def rgb(self,v):
		return self.r(v), self.g(v), self.b(v)
		
	def wxColor(self,v,alpha=wx.ALPHA_OPAQUE):
		return wx.Color(self.r(v), self.g(v), self.b(v),alpha)
		

##############################
### Vizualize Graph like Structures
##############################


class VGraphWin(wx.Window):
	def __init__(self,parent,graph,Wmin=0.0,Wmax=1.0,logicalBounds=None):
		"""
		parent,					Parent wx-object
		iterNodeLabels=[],		iterable for the unique node labels 
		iterNodeXY=[],			iterable for the node positions -- (x,y) tuples, respectively
		iterNodeAct=[],			iterable for the node activations
		iterConnWeights=[]		iterable for the successor connectons of each node
								for each node, an iterable should be returned itself the items of which represent
								connection target node and weight. 
								for example: [[('a',0.4),('x',0.3)],[],[('x',0.7)]] 
								the first node is connected with 'a' and 'x' with the weights 0.4 and 0.3, respectively
								the second node has no successors and the third has 'x' as successor with weight 0.7.
		node: all iterables should produce the same number of items, namely one for each node. the connection weight items
				are iterables themselves. their length depends on the number of successors of the respective node.
		"""
		
		### its a sigmoid :-)
		self.Wsigmo = getSigmoid(Wmin,Wmax)
		
		super(VGraphWin, self).__init__(parent,style=wx.NO_FULL_REPAINT_ON_RESIZE)

		### input independent stuff
		self.rad = 5
		self.colmap = Heatmap() 
		
		### graph specific stuff
		self.graph = graph
		
		### get the boundaries of the graph coordinates (="logical coordinates")
		if logicalBounds == None:
			self.maxx = max( map(lambda (x,y):x , self.xy) )
			self.maxy = max( map(lambda (x,y):y , self.xy) )
			self.minx = min( map(lambda (x,y):x , self.xy) )
			self.miny = min( map(lambda (x,y):y , self.xy) )
		else:
			self.minx,self.miny,self.maxx,self.maxy = logicalBounds

		self.makeMenu()
		self.bindEvents()
		self.initBuffer()
	
	###
	### initialization
	###
	def bindEvents(self):
		for event, handler in [ \
#		   (wx.EVT_LEFT_DOWN, self.onLeftDown), # Start drawing
#				(wx.EVT_LEFT_UP, self.onLeftUp),     # Stop drawing 
#				(wx.EVT_MOTION, self.onMotion),      # Draw
				(wx.EVT_RIGHT_UP, self.onRightUp),   # Popup menu
				(wx.EVT_SIZE, self.onSize),          # Prepare for redraw
				(wx.EVT_IDLE, self.onIdle),          # Redraw
				(wx.EVT_PAINT, self.onPaint),        # Refresh
				(wx.EVT_WINDOW_DESTROY, self.cleanup)]:
			self.Bind(event, handler)

	def initBuffer(self):
		''' Initialize the bitmap used for buffering the display. '''
		size = self.GetClientSize()
		self.buffer = wx.EmptyBitmap(size.width, size.height)
		dc = wx.BufferedDC(None, self.buffer)
		dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
		dc.Clear()

		### setup the transformer to map between device and logical coordinates
		self.tr = Transformer2D( (self.minx,self.miny) , (self.maxx,self.maxy) , \
								   (self.rad,self.rad) , (size.width-self.rad,size.height-self.rad) )

		self.drawGraph(dc)
		self.reInitBuffer = False
		self.dc = dc
	
	def cleanup(self, event):
		if hasattr(self, "menu"):
			self.menu.Destroy()
			del self.menu

	###
	### Drawing
	###
		
		
	def drawGraph(self,dc):
		print ("drawGraph(%s)" % dc)
		dc.BeginDrawing()
		dc.Clear()
		
		cmap = Heatmap(0,500)
		for i in range(500):
			dc.SetPen( wx.Pen(cmap.wxColor(i), 1, wx.SOLID) )
			dc.DrawLine(10+i,0,10+i,10)

		for n,p,a in zip(self.graph.iterNodes(),self.graph.iterXY(),self.graph.iterActivations()):
			dc.SetTextForeground(wx.Color(100,100,100))
			##dc.SetTextBackground(wx.Color(30,30,30))
			x,y = self.tr.pAB(p)
 			brush = wx.Brush(self.colmap.wxColor(a), wx.SOLID)
			dc.SetBrush(brush)
			dc.DrawCircle(x,y,self.rad)
			#print ((n,p,a))
			dc.DrawLabel(n, wx.Rect(x+self.rad,y+self.rad,self.rad, self.rad), 
						alignment=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, indexAccel=-1)

		it = self.graph.iterConnections()
		#print((it,type(it)))
		for n,m,w in it:
			xn,yn = self.graph.getNodePos(n)
			xm,ym = self.graph.getNodePos(m)
			alpha = atan2(xm-xn,ym-yn)		## the angle of the connection in node n
			pn =  ( self.tr.xAB(xn) + sin(alpha)*10 , self.tr.yAB(yn) + cos(alpha)*10 )
			pm =  ( self.tr.xAB(xm) - sin(alpha)*10 , self.tr.yAB(ym) - cos(alpha)*10 )
			print ((n,m,w))
 			pen = wx.Pen(wx.Color(20,20,200,self.Wsigmo(w)*255),max(1,self.Wsigmo(w)*10), wx.SOLID)
			dc.SetPen(pen)
			dc.DrawLinePoint(pn,pm)
		dc.EndDrawing()
		#print "drawGraph... done."


	def makeMenu(self):
		''' Make a menu that can be popped up later. '''
		self.menu = wx.Menu()
		#menu.Append(menuId, str(item), kind=wx.ITEM_CHECK)
		menuID = wx.NewId()
		self.menu.Append(menuID, "ContextMenu", "Bla")
		self.Bind(wx.EVT_MENU, self.onTestHandler, id=menuID)

	def refresh(self):
		dc = wx.BufferedPaintDC(self, self.buffer)
		self.drawGraph(dc)
		

	###
	### event handlers
	###
	def onTestHandler(self, event):
		print ("TestHandler: %s" % event)


	def onRightUp(self, event):
		''' Called when the right mouse button is released, will popup
			the menu. '''
		self.PopupMenu(self.menu)


	def onSize(self, event):
		''' Called when the window is resized. We set a flag so the idle
			handler will resize the buffer. '''
		self.reInitBuffer = True

	def onIdle(self, event):
		''' If the size was changed then resize the bitmap used for double
			buffering to match the window size.  We do it in Idle time so
			there is only one refresh after resizing is done, not lots while
			it is happening. '''
		if self.reInitBuffer:
			self.initBuffer()
			self.Refresh(False)

	def onPaint(self, event):
		''' Called when the window is exposed. '''
		dc = wx.BufferedPaintDC(self, self.buffer)
		#dc = wx.AutoBufferedPaintDC(self)
		self.drawGraph(dc)
		

	# These two event handlers are called before the menu is displayed
	# to determine which items should be checked.
	def onCheckMenuColours(self, event):
		colour = self.idToColourMap[event.GetId()]
		event.Check(colour == self.currentColour)

	def onCheckMenuThickness(self, event):
		thickness = self.idToThicknessMap[event.GetId()]
		event.Check(thickness == self.currentThickness)

	# Event handlers for the popup menu, uses the event ID to determine
	# the colour or the thickness to set.
	def onMenuSetColour(self, event):
		self.currentColour = self.idToColourMap[event.GetId()]

	def onMenuSetThickness(self, event):
		self.currentThickness = self.idToThicknessMap[event.GetId()]

##############################
### Embed Calculations in Interactive Applications
### play / stop / step -- player like control windows etc.
### nice for simulations and step wise calculations
##############################


class TrigCalc(object):
	""" Encapsulate some calculation processor to be triggered from the gui in a step by step fasion."""
	 
	def __init__(self):
		""" doneFeedbackFn() is called after some calculation took place. 
			Can be used to trigger other data structures or vizualisaton updating."""
		self.steps = 1
	
	def calcStep(self):
		""" overload this method for your personal calculation step """
		pass
	
	def calcNSteps(self):
		""" called by the controler application window when calculation step(s) have to be performed """
		for i in range(self.steps):
			self.calcStep()
	
	def getSteps(self):
		return self.steps
	
	def setSteps(self,n):
		""" How many steps should be performed at for each call of calcNSteps? """
		if (type(n) != int and type(n) != long) or n < 1:
			raise ValueError, ("steps must be a positive integer/long. fount %s instead." % n)

		self.steps = n
		
			
class TrigCalcFrame(wx.Frame):
	def __init__(self, calc, parent=None):
		super(TrigCalcFrame,self).__init__(parent)

		### setup gui elements
		pnl = wx.Panel(self)
		#self.checkboxUseDelayed = wx.CheckBox(pnl, -1, "Using delayedresult")
		self.buttonStart = wx.Button(pnl, -1, "Start")
		#self.buttonStop = wx.Button(pnl, -1, "stop")
		self.buttonStepsN = wx.Button(pnl, -1, "N Steps")
		self.slider = wx.Slider(pnl, -1, 100, 1, 1000, size=(100,-1),
								style=wx.SL_HORIZONTAL)
		self.textSteps = wx.TextCtrl(pnl, -1, "1")

		vsizer = wx.BoxSizer(wx.VERTICAL)
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		#vsizer.Add(self.checkboxUseDelayed, 0, wx.ALL, 10)
		hsizer.Add(self.buttonStart, 0, wx.ALL, 5)
		#hsizer.Add(self.buttonStop, 0, wx.ALL, 5)
		hsizer.Add(self.slider, 0, wx.ALL, 5)
		hsizer.Add(self.buttonStepsN, 0, wx.ALL, 5)
		hsizer.Add(self.textSteps, 0, wx.ALL, 5)
		vsizer.Add(hsizer, 0, wx.ALL, 5)
		pnl.SetSizer(vsizer)
		vsizer.SetSizeHints(self)
		
		### bind events
		self.Bind(wx.EVT_BUTTON, self.handleStart, self.buttonStart)
		#self.Bind(wx.EVT_BUTTON, self.handleStop, self.buttonStop)
		self.Bind(wx.EVT_BUTTON, self.handleStepsN, self.buttonStepsN)
		self.Bind(wx.EVT_IDLE, self.onIdle)

		self.Bind(wx.EVT_TIMER, self.onTimeout)

		### init controlling states
		self.run=False
		self.wait=False

		self.t1 = wx.Timer(self)
		self.calc = calc
		self.ct = 0

	###
	### event handlers
	###
	def handleStart(self, event): 
		if not self.run:
			print "start"
			try:
				self.calc.setSteps(int(self.textSteps.GetValue()))
			except(ValueError):
				print "Steps value invalid!"
			self.buttonStart.SetLabel("Stop")
			#self.buttonStart.Enable(False)
			#self.buttonStop.Enable(True)
			
			self.run=True
			self.calcEndless()
		else:
			print "stop"
			self.t1.Stop()
			self.buttonStart.SetLabel("Start")
			#self.buttonStop.Enable(False)
			self.run=False

	def handleStop(self, event): 
		self.buttonStart.Enable(True)
		self.buttonStop.Enable(False)
		self.run=False

	def handleStepsN(self, event):
		self.calcSteps()
		
	def onTimeout(self,evt):
#		self.wait=False
		self.calcEndless()
		
	def calcEndless(self):
		self.calcSteps()
		print ("next %d steps in %d msecs" % (self.calc.getSteps(),self.slider.GetValue()))
		self.t1.Start(self.slider.GetValue())

	def calcSteps(self):
		self.calc.setSteps(int(self.textSteps.GetValue()))
		self.calc.calcNSteps()

	def onIdle(self, event):
#		print "idle %d" % self.ct
#		self.ct += 1
		#if self.run and not self.wait:
		pass



##############################
### Demos for Running the stuff
##############################


class VFrame(wx.Frame):
    def __init__(self,iterNodeLabels,iterConnWeights,iterNodeXY=None,iterNodeAct=None,parent=None,):
        super(VFrame, self).__init__(parent, title="Vizualization Window",
            size=(800,600),
            style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)
        vizwin = VGraphWin(self,iterNodeLabels,iterConnWeights,iterNodeXY,iterNodeAct)

def demo():
	app = wx.App(redirect=False)
	#frame = VFrame( ['a','b','c','d'] , [('a','b',0.3),('a','c',.1),('c','b',.8),] , [(10,20),(13,50),(40,40),(50,50)] , [0.0,0.0,0.0])
	frame = VFrame( ['a','b','c','d','e','f','g','h','i','j','k'], 
					[], 
					[(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(8,0),(9,0),(10,0)] , 
					[0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
	frame.Show()
	app.MainLoop()
 

#class ActivationSpreaderApp(WApp):	
#	def __init__(self):
#		super(ActivationSpreaderApp,self).__init__()
#		
#		self.Bind(wx.EVT_KEY_DOWN, self.onTestHandler)
#
#		frame = VFrame( ['a','b','c','d','e','f','g','h','i','j','k'], 
#						[], 
#						[(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(8,0),(9,0),(10,0)] , 
#						[0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
#		self.addTopFrame(frame)
#		frame.Show()
#
#	def onTestHandler(self, evt):
#		print ("TestHandler: %s" % evt)
#


######################################################
### demo for an interactive calculation application
######################################################
class TestCalc(TrigCalc):
	def __init__(self):
		self.counter = 0
		
	def calcStep(self):
		print ("jetzt %d" % self.counter)
		self.counter == self.counter +1 


class TestApp(WApp):
	def __init__(self):
		WApp.__init__(self)
		self.calc = TestCalc()
		frame = TrigCalcFrame(self.calc)
		self.addTopFrame(frame)
		frame.Show()

def demoTCalc():
	app = TestApp()
	app.MainLoop()
						

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

#################
#### menu kram
#################

		#self.idToColourMap = self.addCheckableMenuItems(self.menu,
		#	self.colours)
		#self.bindMenuEvents(menuHandler=self.onMenuSetColour,
		#	updateUIHandler=self.onCheckMenuColours,
		#	ids=self.idToColourMap.keys())
		#self.menu.Break() # Next menu items go in a new column of the menu
		#self.idToThicknessMap = self.addCheckableMenuItems(self.menu,
		#	self.thicknesses)
		#self.bindMenuEvents(menuHandler=self.onMenuSetThickness,
		#	updateUIHandler=self.onCheckMenuThickness,
		#	ids=self.idToThicknessMap.keys())
		

#	@staticmethod
#	def addCheckableMenuItems(menu, items):
#		''' Add a checkable menu entry to menu for each item in items. This
#			method returns a dictionary that maps the menuIds to the
#			items. '''
#		idToItemMapping = {}
#		for item in items:
#			menuId = wx.NewId()
#			idToItemMapping[menuId] = item
#			menu.Append(menuId, str(item), kind=wx.ITEM_CHECK)
#		return idToItemMapping

#	def bindMenuEvents(self, menuHandler, updateUIHandler, ids):
#		''' Bind the menu id's in the list ids to menuHandler and
#			updateUIHandler. '''
#		sortedIds = sorted(ids)
#		firstId, lastId = sortedIds[0], sortedIds[-1]
#		for event, handler in \
#		   [(wx.EVT_MENU_RANGE, menuHandler),
#				 (wx.EVT_UPDATE_UI_RANGE, updateUIHandler)]:
#			self.Bind(event, handler, id=firstId, id2=lastId)

#################
#### on event kram
#################

#	def onLeftDown(self, event):
#		''' Called when the left mouse button is pressed. '''
#		self.currentLine = []
#		self.previousPosition = event.GetPositionTuple()
#		self.CaptureMouse()

#	def onLeftUp(self, event):
#		''' Called when the left mouse button is released. '''
#		if self.HasCapture():
#			self.lines.append((self.currentColour, self.currentThickness,
#				self.currentLine))
#			self.currentLine = []
#			self.ReleaseMouse()

#	def onMotion(self, event):
#		''' Called when the mouse is in motion. If the left button is
#			dragging then draw a line from the last event position to the
#			current one. Save the coordinants for redraws. '''
#		if event.Dragging() and event.LeftIsDown():
#			dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
#			currentPosition = event.GetPositionTuple()
#			lineSegment = self.previousPosition + currentPosition
#			self.drawLines(dc, (self.currentColour, self.currentThickness,
#				[lineSegment]))
#			self.currentLine.append(lineSegment)
#			self.previousPosition = currentPosition


#################
#### drawing stuff
#################

#	@staticmethod
#	def drawLines(dc, *lines):
#		''' drawLines takes a device context (dc) and a list of lines
#		as arguments. Each line is a three-tuple: (colour, thickness,
#		linesegments). linesegments is a list of coordinates: (x1, y1,
#		x2, y2). '''
#		dc.BeginDrawing()
#		for colour, thickness, lineSegments in lines:
#			pen = wx.Pen(wx.NamedColour(colour), thickness, wx.SOLID)
#			dc.SetPen(pen)
#			for lineSegment in lineSegments:
#				dc.DrawLine(*lineSegment)
#		dc.DrawCircle(20,20,10)
#		dc.EndDrawing()
#
