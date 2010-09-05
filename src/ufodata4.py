import sys
import os
import time
import struct

import pygame
from pygame.locals import *

def getpalette(palette_file):
    # A palette is 256 entries of 3 bytes + 6 additional bytes
    # See http://ufopaedia.org/index.php?title=PALETTES.DAT
    data = palette_file.read (256*3+6)
    if data == '':
        return
    palette = []
    for i in range(0, 255):
        (r, g, b) = struct.unpack_from('BBB', data,  i*3)
        #palette.append((r,  g,  b))
        # palette contains values 0..63 so boost them here to get full brightness
        palette.append((r*4,  g*4,  b*4))
    return palette

def getpalettes(palette_path):
    palette_file = open(palette_path,  'rb')
    eof = False
    palettes = []
    while not eof:
        palette = getpalette(palette_file)
        if palette != None:
            palettes.append(palette)
        else:
            eof = True
    palette_file.close()
    return palettes

def getimages(tab_path,  pck_path, palettes):
    tab_file = open(tab_path, "rb")
    tab_size = os.path.getsize(tab_path)
    
    unpack_format = '<' + str(tab_size/2) + 'H'
  
    tab_filedata = tab_file.read()
    offsets = struct.unpack(unpack_format, tab_filedata)
    tab_file.close()
    
    pck_file = open(pck_path, "rb")
    #for value in offsets:
        #pck_file.seek(value)
    pck_file.seek(offsets[0])   

    
    numofimg = len(offsets)
    images = []
    
    for img in range(numofimg):
        imgsur = pygame.Surface((32, 40),  depth=8)
        imgsur.set_palette(palettes[4])
        imgarray = pygame.PixelArray(imgsur)
        
        blank_byte = pck_file.read(1)
        blank_int = struct.unpack('B', blank_byte)
        blank_int = blank_int[0]
    
        xcount,  ycount = 0, blank_int
    
        done = False
        rle = False
        while not done:
            byte = struct.unpack('B', pck_file.read(1))
            byte = byte[0]
            if rle == True:
                xcount = xcount + byte
                rle = False
            elif byte == 255:
                done = True
            elif byte == 254:
                rle = True
            else:
                imgarray[xcount][ycount] = (byte)
                xcount = xcount + 1
            
            if xcount >= 32:
                ycount = ycount + xcount/32
                xcount = xcount%32
            
        del(imgarray)    
        images.append(imgsur)
    
    pck_file.close()
    return images
    


    #print
    #print binascii.b2a_hex(file.read(2))

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Usage: ufodata4.py tab_path pck_path pallet_path Outputs: image.bmp'
        exit()
    tab_path = sys.argv[1]
    pck_path = sys.argv[2]
    pal_path = sys.argv[3]
    
    pygame.init()
    screen = pygame.display.set_mode((100, 100))
    pygame.display.set_caption('Demo')

    palettes = getpalettes(pal_path)
    images = getimages(tab_path,  pck_path, palettes)
    
    pygame.display.set_mode((50, 100))
    thedisp = pygame.display.get_surface()

    thedisp = pygame.Surface((32*len(images), 40))
    thedisp.fill((0, 0, 0))
    x = 0
    for img in images:
        thedisp.blit(img,  (x,0))
        x = x + 32
    pygame.image.save(thedisp,  'images.BMP') 
    pygame.display.flip()
    pygame.event.pump()
        
    

