
""" 
Set up the plot figures, axes, and items to be done for each frame.

This module is imported by the plotting routines and then the
function setplot is called to set the plot parameters.
    
""" 

from __future__ import absolute_import
from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt

from clawpack.geoclaw import topotools
from six.moves import range

x0 = 0; y0 = 60.

outdir_1d = '1d_latitude/_output'

#--------------------------
def setplot(plotdata=None):
#--------------------------
    
    """ 
    Specify what is to be plotted at each frame.
    Input:  plotdata, an instance of pyclaw.plotters.data.ClawPlotData.
    Output: a modified version of plotdata.
    
    """ 


    from clawpack.visclaw import colormaps, geoplot
    from numpy import linspace

    if plotdata is None:
        from clawpack.visclaw.data import ClawPlotData
        plotdata = ClawPlotData()


    plotdata.clearfigures()  # clear any old figures,axes,items data
    plotdata.format = 'ascii'    # 'ascii' or 'binary' to match setrun.py


    # To plot gauge locations on pcolor or contour plot, use this as
    # an afteraxis function:

    def addgauges(current_data):
        from clawpack.visclaw import gaugetools
        gaugetools.plot_gauge_locations(current_data.plotdata, \
             gaugenos='all', format_string='ko', add_labels=True)
    

    #-----------------------------------------
    # Figure for surface
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='Surface', figno=0)
    plotfigure.facecolor = 'w'

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes('pcolor')
    plotaxes.title = 'Surface'
    plotaxes.aspect_latitude = y0
    plotaxes.xlabel = 'longitude'
    plotaxes.ylabel = 'latitude'
    plotaxes.title = 'Surface at time h:m:s'
    plotaxes.xlimits = [-40,40]
    plotaxes.ylimits = [40,80]


    # Water
    plotitem = plotaxes.new_plotitem(plot_type='2d_imshow')
    #plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    plotitem.plot_var = geoplot.surface_or_depth
    #plotitem.pcolor_cmap = geoplot.tsunami_colormap
    #plotitem.pcolor_cmin = -0.3
    #plotitem.pcolor_cmax = 0.3

    plotitem.imshow_cmap = geoplot.tsunami_colormap
    plotitem.imshow_cmin = -0.3
    plotitem.imshow_cmax = 0.3
    plotitem.add_colorbar = True
    plotitem.colorbar_extend = 'both'
    plotitem.amr_celledges_show = [0,0,0]
    plotitem.patchedges_show = 0

    plotitem = plotaxes.new_plotitem(plot_type='2d_contour')
    #plotitem.show = False
    plotitem.plot_var = geoplot.surface_or_depth
    plotitem.contour_levels = np.linspace(-0.25,0.25,8)
    plotitem.contour_colors = 'k'
    plotitem.amr_contour_show = [0,1,1]

    #-----------------------------------------
    # Figure vs. distance from axis
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='1d', figno=1)
    #plotfigure.show = False
    plotfigure.kwargs = {'figsize': (7,4)}
    plotfigure.figsize = (7,4)
    plotfigure.facecolor = 'w'

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.title = 'Eta vs. distance from axis at time h:m:s'
    plotaxes.xlabel = 'distance (meters)'
    plotaxes.ylabel = 'meters'
    plotaxes.xlimits = [0,3e6]
    #plotaxes.ylimits = [-1.25,0.75] # for t=5hrs
    plotitem = plotaxes.new_plotitem(plot_type='1d_from_2d_data')

    def r_eta(current_data):
        from clawpack.geoclaw.util import haversine
        from pylab import where, nan
        q = current_data.q
        x = current_data.x
        y = current_data.y
        eta = q[3,:,:]
        r = haversine(x0,y0,x,y)
        return r,eta

    plotitem.map_2d_to_1d = r_eta
    plotitem.color = 'b'
    plotitem.kwargs = {'linestyle':'none', 'marker':'o', 
                       'fillstyle':'full', 'markersize': 0.5}

    plotitem = plotaxes.new_plotitem(plot_type='1d_from_2d_data')
    
    def y_eta(current_data):
        from pylab import where, nan
        q = current_data.q
        y = current_data.y
        eta = q[3,:,:]
        eta = where(abs(y)<1, eta, nan)
        y = where(abs(y)<1, y, nan)*111e3
        return y,eta

    plotitem.map_2d_to_1d = y_eta
    plotitem.plotstyle = 'b.'
    plotitem.show = False
        
    def aa(current_data):
        from pylab import grid
        grid(True)

    plotaxes.afteraxes = aa

    if outdir_1d:

        def mapc2p_1d(yc):
            """Convert from latitude to meters"""
            yp = (90.-yc) * 111e3
            return yp

        plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
        plotitem.outdir = outdir_1d
        plotitem.plot_var = -1
        plotitem.plotstyle = 'r-'
        plotitem.MappedGrid = True
        plotitem.mapc2p = mapc2p_1d
        

    #-----------------------------------------
    # Figures for gauges
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='Surface at gauges', figno=300, \
                    type='each_gauge')
    plotfigure.clf_each_gauge = True
    plotfigure.show = False

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = 'auto'
    plotaxes.ylimits = 'auto'
    plotaxes.title = 'Surface'

    # Plot surface as blue curve:
    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    plotitem.plot_var = 3
    plotitem.plotstyle = 'b-'

    # Plot topo as green curve:
    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    plotitem.show = False

    def gaugetopo(current_data):
        q = current_data.q
        h = q[0,:]
        eta = q[3,:]
        topo = eta - h
        return topo
        
    plotitem.plot_var = gaugetopo
    plotitem.plotstyle = 'g-'


    #-----------------------------------------
    
    # Parameters used only when creating html and/or latex hardcopy
    # e.g., via pyclaw.plotters.frametools.printframes:

    plotdata.printfigs = True                # print figures
    plotdata.print_format = 'png'            # file format
    plotdata.print_framenos = 'all'          # list of frames to print
    plotdata.print_gaugenos = 'all'          # list of gauges to print
    plotdata.print_fignos = 'all'            # list of figures to print
    plotdata.html = True                     # create html files of plots?
    plotdata.html_homelink = '../README.html'   # pointer for top of index
    plotdata.latex = True                    # create latex file of plots?
    plotdata.latex_figsperline = 2           # layout of plots
    plotdata.latex_framesperline = 1         # layout of plots
    plotdata.latex_makepdf = False           # also run pdflatex?
    plotdata.parallel = True                 # make multiple frame png's at once

    return plotdata

