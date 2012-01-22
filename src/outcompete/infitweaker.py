#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  Infitweaker - Copyright 2012 Alex Kaplan
#  FreeType high-level python API - Copyright 2011 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
#
# -----------------------------------------------------------------------------
import sys
try:
    import pygtk
    pygtk.require("2.0")
except:
    pass

try:
    import gtk
    import gtk.glade
except:
    sys.exit(1)

from freetype import *
import numpy as np
import Image
import StringIO
import os
    
class pyInfitweaker:
    """This is an PyGTK application to create best settings for INFINALITY freetype"""

    def __init__(self):
    
        #Set the Glade file
        self.gladefile = "infitweaker.glade"  
        self.wTree = gtk.glade.XML(self.gladefile, "mainWindow") 
        
        #Get the image to store the preview results
        self.previewImage = self.wTree.get_widget("image1")
        
        
        self.enFilter1 = self.wTree.get_widget("enFilter1")
        self.enFilter2 = self.wTree.get_widget("enFilter2")
        self.enFilter3 = self.wTree.get_widget("enFilter3")
        self.enFilter4 = self.wTree.get_widget("enFilter4")
        self.enFilter5 = self.wTree.get_widget("enFilter5")
        self.enChrome = self.wTree.get_widget("enChrome")
        
        #Create our dictionay and connect it
        dic = {"on_mainWindow_destroy" : self.destroy,
               "on_previewButton_clicked" : self.OnPreview}
        self.wTree.signal_autoconnect(dic)
        
        
    def destroy(self, widget, data=None):
        print "destroy signal occurred"
        gtk.main_quit()
        
    def main(self):
        gtk.main()
                
    def OnPreview(self, widget):
        
        varFilter = self.enFilter1.get_text() + " " + self.enFilter2.get_text() + " " + self.enFilter3.get_text() + " " + self.enFilter4.get_text() + " " + self.enFilter5.get_text()
        varChrome = self.enChrome.get_text()
        os.environ["INFINALITY_FT_CHROMEOS_STYLE_SHARPENING_STRENGTH"] = varChrome
        os.environ["INFINALITY_FT_FILTER_PARAMS"] = varFilter
        I = self.render('Vera.ttf', (1,1), 1.25, True)
        self.previewImage.set_from_pixbuf(gtk.gdk.pixbuf_new_from_array(np.array(I), gtk.gdk.COLORSPACE_RGB, 8))
        
    
    def render(self, filename = "Vera.ttf", hinting = (False,False), gamma = 1.5, lcd=True):
        text = "A Quick Brown Fox Jumps Over The Lazy Dog 0123456789"
    
        W,H,D = 680, 280, 1
        Z = np.zeros( (H,W), dtype=np.ubyte )
        face = Face(filename)
        pen = Vector(5*64, (H-10)*64)
    
        flags = FT_LOAD_RENDER
        #if hinting[1]: flags |= FT_LOAD_FORCE_AUTOHINT
        #else:          flags |= FT_LOAD_NO_HINTING
        if hinting[0]: hres, hscale = 72,    1.0
        else:          hres, hscale = 72*10, 0.1
        if lcd:
            flags |= FT_LOAD_TARGET_LCD
            Z = np.zeros( (H,W,3), dtype=np.ubyte )
            set_lcd_filter( FT_LCD_FILTER_DEFAULT )
    
    
        for size in range(9,23):
            face.set_char_size( size * 64, 0, hres, 72 )
            matrix = Matrix( int((hscale) * 0x10000L), int((0.0) * 0x10000L),
                             int((0.0)    * 0x10000L), int((1.0) * 0x10000L) )
            previous = 0
            pen.x = 5*64
            for current in text:
                face.set_transform( matrix, pen )
                face.load_char( current, flags)
                kerning = face.get_kerning( previous, current, FT_KERNING_UNSCALED )
                pen.x += kerning.x
                glyph = face.glyph
                bitmap = glyph.bitmap
                x, y = glyph.bitmap_left, glyph.bitmap_top
                w, h, p = bitmap.width, bitmap.rows, bitmap.pitch
                buff = np.array(bitmap.buffer, dtype=np.ubyte).reshape((h,p))
                if lcd:
                    Z[H-y:H-y+h,x:x+w/3].flat |= buff[:,:w].flatten()
                else:
                    Z[H-y:H-y+h,x:x+w].flat |= buff[:,:w].flatten()
                pen.x += glyph.advance.x
                previous = current
            pen.y -= (size+4)*64
    
        # Gamma correction
        Z = (Z/255.0)**(gamma)
        Z = ((1-Z)*255).astype(np.ubyte)
        if lcd:
            I = Image.fromarray(Z, mode='RGB')
        else:
            I = Image.fromarray(Z, mode='L')
        return I

    
if __name__ == "__main__":
    tweaker = pyInfitweaker()
    tweaker.main()
