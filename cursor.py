from os.path import join

import pygame
import state

kExit = """
        XXX                     
       X...X                    
      XX...X                    
      XX...X                    
      XX...X                    
      XX...X                    
      XX...X                    
      XX...X XX                 
      XX...XX..X XX             
      XX...X...XX..X            
      XX...X...X...XXX          
     XXX...X...X...X..X         
    XX X...........X..X         
   XX  X...........X..X         
   XX  X..............X         
   XX  X..............X         
   XX.................X         
   XX.................X         
   XXX...............XX         
   XXXX..............X          
    XXXX............XX          
     XXX............X           
      XXX...........X           
      XXXX.........XX           
       XXX.........X            
        XX.........X            
        XX.........X            
        XX.........X            
        XXXXXXXXXXXX            
        XXXXXXXXXXX             
                                
                                """

kZoomIn = """
     XXXXXXXXXXXX               
    XXX........XXX              
   XX....XXXXX...XX             
    X.........X..XX             
   X...........X..XX            
  XX............X.XX            
   X............X.XX            
  XX............X.XX            
   X............X.XX            
  XX............X.XX            
  XX..............XX            
   X..............XX            
   XX............XX             
   XX............XXX            
    XXX........XXX.XX           
      XXXXXXXXXXXX..XX          
        XXXXXXX  XX..XX         
                  XX..XX        
                   XX..XX       
                    XX..XX      
                     XX..XX     
                      XX..XX    
                       XX..XX   
                        XX..XX  
                         XX..XX 
                          XX..X 
                           XX.X 
                            XXX 
                             XX 
                                
                                
                                """
kTurnRight = """
                                
                                
                                
                                
                                
               XXXX             
              XXX.XX            
              XXX..XX           
              XXX...XX          
              XXX....XX         
XXXXXXXXXXXXXXXXX.....XX        
XX.....................XX       
XX......................XX      
XX.......................XX     
XX........................XX    
XX.........................XX   
XX.........................XX   
XX........................XX    
XX.......................XX     
XX......................XX      
XX.....................XX       
XXXXXXXXXXXXXXXXX.....XX        
              XXX....XX         
              XXX...XX          
              XXX..XX           
              XXX.XX            
               XXXX             
                                
                                
                                
                                
                                """

kTurnLeft = """
                                
                                
                                
                                
                                
         XXX                    
        XX.XX                   
       XX..XXX                  
      XX...XXX                  
     XX....XXX                  
    XX.....XXXXXXXXXXXXXXXXXX   
   XX.......................X   
  XX........................X   
 XX.........................X   
XX..........................X   
X...........................X   
X...........................X   
XX..........................X   
 XX.........................X   
  XX........................X   
   XX.......................X   
    XX.....XXXXXXXXXXXXXXXXXX   
     XX....XXX                  
      XX...XXX                  
       XX..XXX                  
        XX.XXX                  
         XXXX                   
                                
                                
                                
                                
                                """

kInventory = """
                                
              XXX               
             XX..XXXX           
          XXXX...XX..X          
         XX..X...X...X          
        XX...X...X...X          
        XX...X...X...X          
         X...X...X...XXXX       
        XX...X...X...XX..X      
        XX...X...X...X...X      
         X...X...X...X...X      
        XX...X...X...X...X      
        XX...X...X...X...X      
 XXXXX   X...X...X...X...X      
XX...XX XX...X...X...X...X      
XX.....XXX...........X...X      
 XXX....XX...............X      
  XXX....................X      
    XX...................X      
     XX..................X      
      X.................X       
      XX................X       
      XXX...............X       
       XXX..............X       
        XXX............X        
         XXX..........X         
          XX.........X          
          XX.........X          
           X.........X          
          XX.........X          
          XX.........X          
          XXXXXXXXXXXX          """

kZoomOut = """
                                
          XXXXXXXX              
          X......X              
          X......X              
         X........X             
         X........X             
         X........X             
        X..........X            
        X..........X            
        X..........X            
       X............X           
       X............X           
       X............X           
XXXXXXXX............XXXXXXXX    
X..........................X    
XX........................XX    
XXX......................XXX    
 XXX....................XXXX    
 XXXX..................XXXX     
  XXXX................XXXX      
   XXXX..............XXXX       
    XXXX............XXXX        
     XXXX..........XXXX         
      XXXX........XXXX          
       XXXX......XXXX           
        XXXX....XXXX            
         XXXX..XXXX             
          XXXXXXXX              
           XXXXXX               
            XXXX                
                                
                                """

kPhone = """
                                
                                
                                
                                
         XXXXXXXXXXXXXX         
    XXXXXX.............XXXXX    
   XX.......................X   
  XX.........................X  
 XX...........................X 
XX............XXXXX............X
 X........X..XXXXXXX..X........X
XX.......XX...........XX.......X
XXXXXXX.XXX...........XXX.XXXXXX
 X......XX.............XX......X
XXXXXXXXX.....XXXXX.....XXXXXXXX
 XXXXXXXX....XXXXXXX....XXXXXXX 
      XX....XXXXXXXXX....X      
      XX....XXXXXXXXX....X      
     XX.....XXXXXXXXX.....X     
      X.....XXXXXXXXX.....X     
     XX.....XXXXXXXXX.....X     
    XX.......XXXXXXX.......X    
    XX........XXXXX........X    
    XX.....................X    
    XX.....................X    
    XXX...................X     
     XXXXXXXXXXXXXXXXXXXXX      
                                
                                
                                
                                
                                """
def load_cursors():
    cursors = dict()

    compile_args = ("X", ".", "o") 
    xors,ands = pygame.cursors.compile(kExit.split("\n")[1:], *compile_args) 
    cursors['kExit'] = (32,32), (0,0), xors, ands

    xors,ands = pygame.cursors.compile(kZoomIn.split("\n")[1:], *compile_args) 
    cursors['kZoomIn'] = (32,32), (0,0), xors, ands

    xors,ands = pygame.cursors.compile(kZoomOut.split("\n")[1:], *compile_args) 
    cursors['kZoomOut'] = (32,32), (0,0), xors, ands

    xors,ands = pygame.cursors.compile(kTurnRight.split("\n")[1:], *compile_args) 
    cursors['kTurnRight'] = (32,32), (0,0), xors, ands

    xors,ands = pygame.cursors.compile(kTurnLeft.split("\n")[1:], *compile_args) 
    cursors['kTurnLeft'] = (32,32), (0,0), xors, ands
    
    xors,ands = pygame.cursors.compile(kInventory.split("\n")[1:], *compile_args) 
    cursors['kInventory'] = (32,32), (0,0), xors, ands

    xors,ands = pygame.cursors.compile(kPhone.split("\n")[1:], *compile_args) 
    cursors['kPhone'] = (32,32), (0,0), xors, ands
 
    return cursors
