#! /usr/bin/python
#
# Copyright 2012 Edo Mangelaars
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import curses.wrapper, time, random, sys

random.seed()
FPS = 5

###### OBJECTS

class gameobject:
   posx = 0
   posy = 0
   sizex = 1
   sizey = 1
   color = 7
   pathfindingqueue = []
   def step(self, objects):
      pass
   def key(self, c):
      pass

class enemy(gameobject):
   color = 6
   def step(self, objects):
      debug("E stepped")
      p = next(filter(lambda obj: isinstance(obj, player), objects))
      if self.posx == p.posx and self.posy == p.posy:
         p.alive = False
      self.posx, self.posy = steptowards(self, p, objects)
      self.pathfindingqueue = []

class player(gameobject):
   color = 8
   direction = 2
   nextdirection = 2
   alive = True
   def step(self, objects):
      debug("P stepped")
      for i in objects:
         if isinstance(i, enemy) and i.posx == self.posx and i.posy == self.posy:
            self.alive = False
      if self.alive == False:
         return

      newposx, newposy = calcdir(self.posx, self.posy, self.nextdirection)
      for obj in objects:
         if obj.posx == newposx and obj.posy == newposy:
            if isinstance(obj, wall):
               newposx, newposy = calcdir(self.posx, self.posy, self.direction)
               break
      else:
         self.direction = self.nextdirection

      for obj in objects:
         if obj.posx == newposx and obj.posy == newposy:
            if isinstance(obj, pellet):
               obj.geteaten()
            elif isinstance(obj, wall):
               return
      self.posx = newposx
      self.posy = newposy
      self.pathfindingqueue = []

   def key(self, c):
      if   c == curses.KEY_LEFT : self.nextdirection = 0
      elif c == curses.KEY_UP   : self.nextdirection = 1
      elif c == curses.KEY_RIGHT: self.nextdirection = 2
      elif c == curses.KEY_DOWN : self.nextdirection = 3

class wall(gameobject):
   color = 2

class pellet(gameobject):
   color = 7
   def geteaten(self):
      self.color = 0

class power(gameobject):
   color = 4

def calcdir(x, y, dir):
   if   dir == 0: x -= 1
   elif dir == 1: y -= 1
   elif dir == 2: x += 1
   elif dir == 3: y += 1
   return (x, y)

def steptowards(me, him, objects):
   begintime = time.time()

   fromx, fromy = me.posx, me.posy
   tox, toy = him.posx, him.posy

   if (fromx, fromy) == (tox, toy):
      debug("That took %.2f seconds" % (time.time() - begintime))
      return (fromx, fromy)

   if len(him.pathfindingqueue) == 0:
         him.pathfindingqueue.append((tox,toy,0))
      
   while True:
      
      found = False
      for i in him.pathfindingqueue:
         if i[0] == fromx and i[1] == fromy:
            found = True
      if found == True:
         break
      
      tempqueue = []
      for element in him.pathfindingqueue:
         cells = [(element[0]-1,element[1],element[2]+1),
                  (element[0],element[1]-1,element[2]+1),
                  (element[0]+1,element[1],element[2]+1),
                  (element[0],element[1]+1,element[2]+1)]
         toadd = []
         for cell in cells:
            add = True
            for obj in objects:
               if obj.posx == cell[0] and obj.posy == cell[1] and isinstance(obj, wall):
                  add = False
            if add == True:
               for el in him.pathfindingqueue:
                  if el[0] == cell[0] and el[1] == cell[1] and el[2] <= cell[2]:
                     add = False
            if add == True:
               toadd.append(cell)
         tempqueue.extend(toadd)
      him.pathfindingqueue.extend(tempqueue)
         

   possiblemoves = []
   for el in him.pathfindingqueue:
      if  (el[0] == fromx+1 and el[1] == fromy) or (el[0] == fromx and el[1] == fromy+1) or (el[0] == fromx-1 and el[1] == fromy) or (el[0] == fromx and el[1] == fromy-1):
         possiblemoves.append(el)
   lowest = sorted(possiblemoves, key = lambda move: move[2])[0]

   debug("That took %.2f seconds" % (time.time() - begintime))

   return(lowest[0], lowest[1])






###### GAME METHODS

def init():
   objects = []
   level = open("level", mode="rt", encoding="utf-8").read(None).splitlines()
   for (i, row) in enumerate(level):
      for (j, column) in enumerate(row):
         obj = {
               'W': wall(),
               '.': pellet(),
               '1': enemy(),
               #'2': enemy(),
               #'3': enemy(),
               #'4': enemy(),
               'P': player(),
               '*': power()
         }.get(column, None)
         if obj != None:
            obj.posx = j
            obj.posy = i
            objects.append(obj)

   objects = sorted(objects, key = lambda obj:
         1 if isinstance(obj, player) else 2 if isinstance(obj, enemy) else 0
      )
   return objects

def gameloop(objects):
   for obj in objects:
      obj.step(objects)
   return objects

def keypress(objects, c):
   for obj in objects:
      obj.key(c)

def draw(objects, scr):
   scr.erase()
   for obj in objects:
      for x in range(obj.posx * 4, obj.posx * 4 + obj.sizex):
         for y in range(obj.posy * 2, obj.posy * 2 + obj.sizey):
            try:
               if obj.color > 0:
                  if isinstance(obj, pellet):
                     i = " .  "
                     j = "    "
                  else:
                     i = "████"
                     j = "████"
               else:
                  i = "    "
                  j = "    "
               scr.addstr(y, x, i, curses.color_pair(obj.color))
               scr.addstr(y+1, x, j, curses.color_pair(obj.color))
            except Exception as e:
               debug(str(e))
               raise
   for (i, message) in enumerate(debuglist):
      scr.addstr(45+i, 0, message, curses.color_pair(7))
   scr.refresh()

###### FRAMEWORK

debuglist = []

def debug(message):
   debuglist.append(message)

def gamestep(objects, scr):
   begintime = time.time()
   global debuglist
   debuglist = []
   gameloop(objects)
   draw(objects, scr)
   while True:
      c = scr.getch()
      if c != -1:
         keypress(objects, c)
      if time.time() - begintime > 1/FPS:
         break

def game(scr):
   curses.use_default_colors()
   curses.curs_set(0)
   curses.cbreak()
   scr.nodelay(True)
   curses.init_pair(1, curses.COLOR_BLACK, -1)
   curses.init_pair(2, curses.COLOR_BLUE,  -1)
   curses.init_pair(3, curses.COLOR_CYAN,  -1)
   curses.init_pair(4, curses.COLOR_GREEN, -1)
   curses.init_pair(5, curses.COLOR_MAGENTA, -1)
   curses.init_pair(6, curses.COLOR_RED,   -1)
   curses.init_pair(7, curses.COLOR_WHITE, -1)
   curses.init_pair(8, curses.COLOR_YELLOW,-1)
   objects = init()
   for i in objects:
      if isinstance(i, player):
         p = i
         break
   draw(objects, scr)
   while True:
      if p.alive == False:
         break
      gamestep(objects, scr)

curses.wrapper(game)
