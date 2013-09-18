'''

A clone of ... something ... with the kivy framework

intro sound http://www.freesound.org/people/ERH/sounds/42286/
water sound http://www.freesound.org/people/junggle/sounds/30342/
Image credit: NASA/JPL-Caltech

'''

import os
import sys
import re
import pickle
import math

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.scatter import Scatter
from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition, WipeTransition, SwapTransition, ShaderTransition
from kivy.garden.moretransitions import PixelTransition, RippleTransition, BlurTransition, RVBTransition, RotateTransition
from functools import partial

class Splash(Screen):
	pass

class Menu(Screen):
	pass

class Help(Screen):
	pass

class Game(Screen):
	score = NumericProperty(0)

class ElementButton(Button):
	text= StringProperty('')

class Element(Scatter):
	text = StringProperty('')
	color = ListProperty([1,1,1,1])

class Transmut(App):
	
	elements_found = ['Air', 'Earth', 'Fire', 'Water']
	ether = []
	universe = []
	
	def build(self):

		self.data_path = os.path.realpath(os.path.dirname(sys.argv[0])) + os.sep + "Data" + os.sep

		self.load_ether()
	
		#self.test()
		#self.solution()
		
		self.screenManager = ScreenManager(transition=FadeTransition())

		self.splash = Splash(name="splash")
		self.menu   = Menu(name="menu")
		self.help   = Help(name="help")
		self.game   = Game(name="game")
		
		self.screenManager.add_widget(self.splash)
		self.screenManager.add_widget(self.menu)
		self.screenManager.add_widget(self.help)
		self.screenManager.add_widget(self.game)
		
		sound_intro = SoundLoader.load(filename= self.data_path + '42286__erh__f-eh-angelic-3.ogg')
		self.sound_find  = SoundLoader.load(filename= self.data_path + '30342__junggle__waterdrop25.ogg')
		
		sound_intro.play()
		
		self.showSplash()
		
		return self.screenManager

	def showSplash(self):
		self.screenManager.current = 'splash'
		
		Animation(
			scale=self.splash.background.scale*1.3, 
			duration=25.0
		).start(self.splash.background)

	def showMenu(self):
		self.screenManager.transition=RippleTransition(duration=2.0)
		self.screenManager.current = 'menu'
		
		Animation(
			scale=self.menu.background.scale*1.3, 
			duration=25.0
		).start(self.menu.background)
		
	def showHelp(self):
		self.screenManager.transition=BlurTransition(duration=2.0)
		self.screenManager.current = 'help'
		
		Animation(
			scale=self.help.background.scale*1.3, 
			duration=25.0
		).start(self.help.background)
		
	

	def newGame(self):
		self.showGame()
		
	def restore_game(self):
		try:
			g = open(self.data_path + 'savegame', 'rb')
			self.elements_found = pickle.load(g)
			g.close()
			self.showGame()
		except:
			self.showHelp()

	def showGame(self):
		
		for e in self.elements_found:
			self.update_elements_menu(e)
		
		self.screenManager.transition=FadeTransition(duration=1.0)
		self.screenManager.current = 'game'


	def update_elements_menu(self,e):
		self.game.elementlist.add_widget(ElementButton(text=e))
		self.game.score = self.game.score + 1

		

	def add_element_to_universe(self,*args):
		e = args[0]
		
		if len(self.universe) > 0:
			#let's roll
			a = 2*math.pi/len(self.universe)
			c = 0
			r = 150 + 100*len(self.universe)/10
			for x in self.universe:
				A = Animation(
					center_x  = Window.center[0] + math.cos(c*a)*r, 
					center_y  = Window.center[1] + math.sin(c*a)*r, 
					transition = 'out_back', 
					duration = 1
				)
				c = c + 1
				A.start(x)

		f = Element(text = e, center=(Window.width,Window.height))
		f.bind(on_touch_up=partial(self.check_position,f))
		f.bind(on_touch_move=partial(self.check_color,f))
		
		self.universe.append(f)	
		self.game.add_widget(f)
		
		A = Animation(
			center  = Window.center,
			transition = 'out_back', 
			duration = 1
		)
		A.start(f)
		
		
		
		

	def check_color(self,*args):
		f = args[1]
		#border => red (delete)
		if f in self.universe and (f.x <0.1*Window.width or f.x>0.9*Window.width or f.y<0.05*Window.height or f.y>0.90*Window.height):
			f.color = [1,0,0.4,1]
		else:
			f.color = [1,1,1,1]

	def check_position(self,*args):
		f = args[1]
		if f in self.universe and (f.x <0.1*Window.width or f.x>0.9*Window.width or f.y<0.05*Window.height or f.y>0.90*Window.height):
			self.universe.remove(f)
			self.game.remove_widget(f)
			return 1
			
		for e in self.universe:
			if e == f:
				continue
			if f.collide_widget(e):
				b = self.transmute(e.text,f.text)
				if b:
					self.sound_find.play()
					self.universe.remove(e)
					self.universe.remove(f)
					self.game.remove_widget(e)
					self.game.remove_widget(f)
					self.add_element_to_universe(b)
					if b not in self.elements_found:
						self.elements_found.append(b)
						output = open(self.data_path + 'savegame', 'wb')
						pickle.dump(self.elements_found, output)
						output.close()						
						self.update_elements_menu(b)
					return 1

	def load_ether(self):
		f = open(self.data_path + "ether.dat", 'r')
		c = 0
		for line in f:
			c = c + 1
			
			if re.match("#",line):
				continue
			
			a = re.match("(\d+)\s+(.*?)\s+\=\s+(.*?)\s+\+\s+(.*?)\s+",line)
			if a != None: 
				self.ether.append( [int(a.group(1)), a.group(2), a.group(3), a.group(4)] )
			else:
				print "Error building ether [%d] " % c


	def transmute(self, item1, item2):
		for formula in self.ether:
			if (formula[2] == item1 and formula[3] == item2) or (formula[3] == item1 and formula[2] == item2):
				return formula[1]
		return None

	def test(self):
		print "%d %s = %s + %s" %(self.ether[5][0], self.ether[5][1], self.ether[5][2], self.ether[5][3])		
		print "transmute Storm & Snow => %s" % self.transmute('Storm','Snow')
		print "transmute Bread & Snow => %s" % self.transmute('Bread','Snow')
	
	# doesn't work
	def solution(self):
		s = ['Air', 'Earth', 'Fire', 'Water']
		count = 4

		def solution_rec(e,l):
			for x in l:
				n = self.transmute(e,x)
				if n and n not in s:
					#count = count + 1;
					print "%s + %s = %s" %(e,x,n)
					l.append(n)
					solution_rec(n,l)
						
		for e in s:
			solution_rec(e,s)
			

#here we go!
if __name__ in ('__android__', '__main__'):
	Transmut().run()


