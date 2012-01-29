'''

A clone of ... something ... with the kivy framework

intro sound http://www.freesound.org/people/ERH/sounds/42286/
water sound http://www.freesound.org/people/junggle/sounds/30342/


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
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.core.audio import SoundLoader
from functools import partial

class Screen(FloatLayout):
	app = ObjectProperty(None)

class Splash(Screen):
	pass

class Menu(Screen):
	pass

class FullImage(Image):
    pass

class Element(Scatter):
	text = StringProperty('')

class Transmut(App):
		
	def build(self):
		
		self.ether = []
		self.universe = []
		self.data_path = os.path.realpath(os.path.dirname(sys.argv[0])) + os.sep + "Data" + os.sep
		self.load_ether()
	
		#self.test()
		#self.solution()
		
		self.root = FloatLayout()
		
		self.screen_menu   = Menu(app=self)
		self.screen_splash = Splash(app=self)
		
		sound_intro = SoundLoader.load(filename= self.data_path + '42286__erh__f-eh-angelic-3.ogg')
		self.sound_find  = SoundLoader.load(filename= self.data_path + '30342__junggle__waterdrop25.ogg')
		
		sound_intro.play()
		
		self.show('splash')

	def show(self, *args):
		name = args[0]
		screen = getattr(self, 'screen_%s' % name)
		self.root.clear_widgets()
		self.root.add_widget(screen)

	def new_game(self):
		self.elements_found = ['Air', 'Earth', 'Fire', 'Water']
		self.game()
		
	def restore_game(self):
		try:
			g = open(self.data_path + 'savegame', 'rb')
			self.elements_found = pickle.load(g)
			g.close()
			self.game()
		except:
			self.new()
		
	def game(self):
		
		self.root.clear_widgets()
		
		a = AnchorLayout()
		i = Image(source = 'Data/space.jpg', allow_stretch = True, keep_ratio =  False)
		a.add_widget(i)
		
		g1 = GridLayout(size_hint = (1,1), cols = 2, rows = 1)
		a.add_widget(g1)
		s = ScrollView(size_hint = (.25, 1), do_scroll_x = False, size_hint_y = None)
		g1.add_widget(s)
		self.g2 = GridLayout(size_hint = (1, None), height = len(self.elements_found)*35, cols = 1, spacing = 2)
		s.add_widget(self.g2)
		
		self.l = Label(text="0/"+str(len(self.ether)+4), size_hint = (None, None), height = 35)
		self.g2.add_widget(self.l)
		for e in self.elements_found:
			self.update_elements_menu(e)
		
		self.root.add_widget(a)

	def update_elements_menu(self,e):
		b = Button(size_hint = (None, None), height = 30, text = e)
		b.bind(on_press = partial(self.add_element_to_universe,e))
		self.g2.add_widget(b)
		self.g2.height = len(self.elements_found)*30
		self.l.text = "%d / %d" % (len(self.elements_found), len(self.ether)+4)

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

		f = Element(text = e, center=Window.center)
		f.bind(on_touch_up=partial(self.check_position,f))
		self.universe.append(f)	
		self.root.add_widget(f)

	def check_position(self,*args):
		f = args[1]
		if f in self.universe and (f.x <0.1*Window.width or f.x>0.9*Window.width or f.y<0.1*Window.height or f.y>0.9*Window.height):
			self.universe.remove(f)
			self.root.remove_widget(f)
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
					self.root.remove_widget(e)
					self.root.remove_widget(f)
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


