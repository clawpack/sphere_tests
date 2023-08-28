
""" 
Set up the plot figures, axes, and items to be done for each frame.

This module is imported by the plotting routines and then the
function setplot is called to set the plot parameters.
    
""" 

import numpy as np
import matplotlib.pyplot as plt
import os

from clawpack.geoclaw import topotools

if 0:
    image = plt.imread('GE_PA2.png')

    def background_image(current_data):
        from pylab import imshow
        extent = [-123.5,-123.33,48.10,48.17]
        imshow(image,extent=extent)

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
    plotdata.format = 'binary'


    # To plot gauge locations on pcolor or contour plot, use this as
    # an afteraxis function:

    def addgauges(current_data):
        from clawpack.visclaw import gaugetools
        gaugetools.plot_gauge_locations(current_data.plotdata, \
             gaugenos='all', format_string='ko', add_labels=True)
    

    def timeformat(t):
        from numpy import mod
        hours = int(t/3600.)
        tmin = mod(t,3600.)
        min = int(tmin/60.)
        sec = int(mod(tmin,60.))
        timestr = '%s:%s:%s' % (hours,str(min).zfill(2),str(sec).zfill(2))
        return timestr

    def title_hours(current_data):
        from pylab import title
        t = current_data.t
        timestr = timeformat(t)
        title('%s after earthquake' % timestr)


    drytol_default = 1e-3

    def surface_or_depth(current_data):
        """
        Modified from geoplot version to use eta = q[-1,:,:], which
        should work for either num_eqn = 3 or 5.
        
        Return a masked array containing the surface elevation where the topo is
        below sea level or the water depth where the topo is above sea level.
        Mask out dry cells.  Assumes sea level is at topo=0.
        Surface is eta = h+topo, assumed to be output as 4th column of fort.q
        files.
        """
        import numpy

        drytol = getattr(current_data.user, 'drytol', drytol_default)
        q = current_data.q
        h = q[0,:,:]
        eta = q[-1,:,:]
        topo = eta - h

        # With this version, the land is transparent.
        surface_or_depth = numpy.ma.masked_where(h <= drytol,
                                                 numpy.where(topo<0, eta, h))

        try:
            # Use mask covering coarse regions if it's set:
            m = current_data.mask_coarse
            surface_or_depth = numpy.ma.masked_where(m, surface_or_depth)
        except:
            pass

        return surface_or_depth

    def land(current_data):
        """
        Return a masked array containing the surface elevation only in dry cells.
        Modified from geoplot version to use eta = q[-1,:,:], which
        should work for either num_eqn = 3 or 5.
        """
        import numpy
        drytol = current_data.user.get('dry_tolerance', drytol_default)
        q = current_data.q
        h = q[0,:,:]
        eta = q[-1,:,:]
        land = numpy.ma.masked_where(h>drytol, eta)
        return land

    def topo(current_data):
        import numpy
        q = current_data.q
        h = q[0,:,:]
        eta = q[-1,:,:]
        topo = eta - h
        return topo


    #-----------------------------------------
    # Figure for surface
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='Surface', figno=21)
    #plotfigure.show = False
    plotfigure.kwargs = {'figsize':(8,7)}
    plotfigure.kwargs['facecolor'] = 'w'

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes('pcolor')
    plotaxes.title = 'Surface'
    plotaxes.scaled = False
    plotaxes.xlimits = [-200,-110]
    plotaxes.ylimits = [11,64]

    def fixup(current_data):
        from pylab import title, ticklabel_format, gca, cos, pi
        import pylab
        #addgauges(current_data)
        t = current_data.t
        t = t / 3600.  # hours
        title('Surface at %4.2f hours' % t, fontsize=10)
        pylab.xticks(fontsize=10)
        pylab.yticks(fontsize=10)
        ticklabel_format(useOffset=False)
        pylab.xticks(rotation=20)
        gca().set_aspect(1./cos(38*pi/180.))
        title_hours(current_data)
    plotaxes.afteraxes = fixup

    # Water
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    #plotitem.plot_var = geoplot.surface
    plotitem.plot_var = surface_or_depth
    plotitem.pcolor_cmap = geoplot.tsunami_colormap
    plotitem.pcolor_cmin = -1. 
    plotitem.pcolor_cmax = 1. 
    plotitem.add_colorbar = True
    plotitem.colorbar_shrink = 0.7
    plotitem.celledges_show = 0
    #plotitem.amr_patchedges_show = [0,0,1]

    # Land
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    plotitem.plot_var = land
    plotitem.pcolor_cmap = geoplot.land1_colormap
    plotitem.pcolor_cmin = 0.0
    plotitem.pcolor_cmax = 2000.0
    plotitem.add_colorbar = False
    plotitem.celledges_show = 0
    #plotitem.amr_patchedges_show = [0,0,1]
    #plotaxes.xlimits = [-120,-60]
    #plotaxes.ylimits = [-60,0]

    # add contour lines of bathy if desired:
    plotitem = plotaxes.new_plotitem(plot_type='2d_contour')
    plotitem.show = False
    plotitem.plot_var = geoplot.topo
    plotitem.contour_levels = linspace(-3000,-3000,1)
    plotitem.amr_contour_colors = ['y']  # color on each level
    plotitem.kwargs = {'linestyles':'solid','linewidths':2}
    plotitem.amr_contour_show = [1,0,0]  
    plotitem.celledges_show = 0
    plotitem.patchedges_show = 0


    #-----------------------------------------
    # Figure for surface
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='Hawaii', figno=2)
    #plotfigure.show = False
    plotfigure.kwargs = {'figsize':(8,7)}

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes('pcolor')
    plotaxes.title = 'Surface'
    plotaxes.scaled = False
    plotaxes.xlimits = [-162,-153]
    plotaxes.ylimits = [18,24]

    def fixup(current_data):
        from pylab import title, ticklabel_format, gca, cos, pi
        import pylab
        #addgauges(current_data)
        t = current_data.t
        t = t / 3600.  # hours
        title('Surface at %4.2f hours' % t, fontsize=10)
        pylab.xticks(fontsize=10)
        pylab.yticks(fontsize=10)
        ticklabel_format(useOffset=False)
        pylab.xticks(rotation=20)
        gca().set_aspect(1./cos(20*pi/180.))
        title_hours(current_data)
    plotaxes.afteraxes = fixup

    # Water
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    #plotitem.plot_var = geoplot.surface
    plotitem.plot_var = surface_or_depth
    plotitem.pcolor_cmap = geoplot.tsunami_colormap
    plotitem.pcolor_cmin = -1. 
    plotitem.pcolor_cmax = 1. 
    plotitem.add_colorbar = True
    plotitem.colorbar_shrink = 0.7
    plotitem.celledges_show = 0
    plotitem.amr_patchedges_show = [0]

    # Land
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    plotitem.plot_var = land
    plotitem.pcolor_cmap = geoplot.land1_colormap
    plotitem.pcolor_cmin = 0.0
    plotitem.pcolor_cmax = 2000.0
    plotitem.add_colorbar = False
    plotitem.celledges_show = 0
    plotitem.amr_patchedges_show = [0]
    #plotaxes.xlimits = [-120,-60]
    #plotaxes.ylimits = [-60,0]

    #-----------------------------------------
    # Figure for surface
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='Big Island', figno=3)
    plotfigure.show = False
    plotfigure.kwargs = {'figsize':(8,7)}

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes('pcolor')
    plotaxes.title = 'Surface'
    plotaxes.scaled = False
    plotaxes.xlimits = [-156, -154.5]
    plotaxes.ylimits = [19.4, 20.5]

    def fixup(current_data):
        from pylab import title, ticklabel_format, gca, cos, pi
        import pylab
        #addgauges(current_data)
        t = current_data.t
        t = t / 3600.  # hours
        title('Surface at %4.2f hours' % t, fontsize=10)
        pylab.xticks(fontsize=10)
        pylab.yticks(fontsize=10)
        ticklabel_format(useOffset=False)
        pylab.xticks(rotation=20)
        gca().set_aspect(1./cos(20*pi/180.))
        title_hours(current_data)
    plotaxes.afteraxes = fixup

    # Water
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    #plotitem.plot_var = geoplot.surface
    plotitem.plot_var = surface_or_depth
    plotitem.pcolor_cmap = geoplot.tsunami_colormap
    plotitem.pcolor_cmin = -1. 
    plotitem.pcolor_cmax = 1. 
    plotitem.add_colorbar = True
    plotitem.colorbar_shrink = 0.7
    plotitem.celledges_show = 0
    plotitem.amr_patchedges_show = [0]

    # Land
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    plotitem.plot_var = land
    plotitem.pcolor_cmap = geoplot.land1_colormap
    plotitem.pcolor_cmin = 0.0
    plotitem.pcolor_cmax = 2000.0
    plotitem.add_colorbar = False
    plotitem.celledges_show = 0
    plotitem.amr_patchedges_show = [0]
    #plotaxes.xlimits = [-120,-60]
    #plotaxes.ylimits = [-60,0]


    #-----------------------------------------
    # Figure for surface
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='Hilo', figno=4)
    plotfigure.show = False
    plotfigure.kwargs = {'figsize':(8,7)}

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes('pcolor')
    plotaxes.title = 'Surface'
    plotaxes.scaled = False
    plotaxes.xlimits = [-155.12, -154.98]
    plotaxes.ylimits = [19.7, 19.8]

    def addgauges_hilo(current_data):
        from clawpack.visclaw import gaugetools
        gaugetools.plot_gauge_locations(current_data.plotdata, \
             gaugenos=[1007,1008,7760], format_string='ko', add_labels=True)
    

    def fixup(current_data):
        from pylab import title, ticklabel_format, gca, cos, pi
        import pylab
        addgauges_hilo(current_data)
        t = current_data.t
        t = t / 3600.  # hours
        title('Surface at %4.2f hours' % t, fontsize=10)
        pylab.xticks(fontsize=10)
        pylab.yticks(fontsize=10)
        ticklabel_format(useOffset=False)
        pylab.xticks(rotation=20)
        gca().set_aspect(1./cos(20*pi/180.))
        title_hours(current_data)
    plotaxes.afteraxes = fixup

    # Water
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    #plotitem.plot_var = geoplot.surface_or_depth
    plotitem.plot_var = surface_or_depth
    plotitem.pcolor_cmap = geoplot.tsunami_colormap
    plotitem.pcolor_cmin = -1. 
    plotitem.pcolor_cmax = 1. 
    plotitem.add_colorbar = True
    plotitem.colorbar_shrink = 0.7
    plotitem.celledges_show = 0
    plotitem.amr_patchedges_show = [0]

    # Land
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    plotitem.plot_var = land
    plotitem.pcolor_cmap = geoplot.land1_colormap
    plotitem.pcolor_cmin = 0.0
    plotitem.pcolor_cmax = 2000.0
    plotitem.add_colorbar = False
    plotitem.celledges_show = 0
    plotitem.amr_patchedges_show = [0]
    #plotaxes.xlimits = [-120,-60]
    #plotaxes.ylimits = [-60,0]

    #-----------------------------------------
    # Figure for surface
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='Laupahoehoe', figno=9)
    plotfigure.show = False
    plotfigure.kwargs = {'figsize':(8,7)}

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes('pcolor')
    plotaxes.title = 'Surface'
    plotaxes.scaled = False
    plotaxes.xlimits = [-155.248, -155.238]
    plotaxes.ylimits = [19.987, 19.998]

    def addgauges_laupahoehoe(current_data):
        from clawpack.visclaw import gaugetools
        gaugetools.plot_gauge_locations(current_data.plotdata, \
             gaugenos=[1010], format_string='ko', add_labels=True)
    

    def fixup(current_data):
        from pylab import title, ticklabel_format, gca, cos, pi
        import pylab
        addgauges_laupahoehoe(current_data)
        t = current_data.t
        t = t / 3600.  # hours
        title('Surface at %4.2f hours' % t, fontsize=10)
        pylab.xticks(fontsize=10)
        pylab.yticks(fontsize=10)
        ticklabel_format(useOffset=False)
        pylab.xticks(rotation=20)
        gca().set_aspect(1./cos(20*pi/180.))
        title_hours(current_data)
    plotaxes.afteraxes = fixup

    # Water
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    #plotitem.plot_var = geoplot.surface_or_depth
    plotitem.plot_var = surface_or_depth
    plotitem.pcolor_cmap = geoplot.tsunami_colormap
    plotitem.pcolor_cmin = -1. 
    plotitem.pcolor_cmax = 1. 
    plotitem.add_colorbar = True
    plotitem.colorbar_shrink = 0.7
    plotitem.celledges_show = 0
    plotitem.amr_patchedges_show = [0]

    # Land
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    plotitem.plot_var = land
    plotitem.pcolor_cmap = geoplot.land1_colormap
    plotitem.pcolor_cmin = 0.0
    plotitem.pcolor_cmax = 2000.0
    plotitem.add_colorbar = False
    plotitem.celledges_show = 0
    plotitem.amr_patchedges_show = [0]
    #plotaxes.xlimits = [-120,-60]
    #plotaxes.ylimits = [-60,0]



    #-----------------------------------------
    # Figure for Maui_13sec
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='Maui_13sec', figno=5)
    plotfigure.show = False
    plotfigure.kwargs = {'figsize':(8,7)}

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes('pcolor')
    plotaxes.title = 'Surface'
    plotaxes.scaled = False
    plotaxes.xlimits = [-156.5125, -156.494]
    plotaxes.ylimits = [20.93,20.9475]

    def fixup(current_data):
        from pylab import title, ticklabel_format, gca, cos, pi
        import pylab
        #addgauges(current_data)
        t = current_data.t
        t = t / 3600.  # hours
        title('Surface at %4.2f hours' % t, fontsize=10)
        pylab.xticks(fontsize=10)
        pylab.yticks(fontsize=10)
        ticklabel_format(useOffset=False)
        pylab.xticks(rotation=20)
        gca().set_aspect(1./cos(20*pi/180.))
        title_hours(current_data)
    plotaxes.afteraxes = fixup

    # Water
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    #plotitem.plot_var = geoplot.surface
    plotitem.plot_var = surface_or_depth
    plotitem.pcolor_cmap = geoplot.tsunami_colormap
    plotitem.pcolor_cmin = -5. 
    plotitem.pcolor_cmax = 5. 
    plotitem.add_colorbar = True
    plotitem.colorbar_shrink = 0.7
    plotitem.celledges_show = 0
    plotitem.amr_patchedges_show = [0]

    # Land
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    plotitem.plot_var = land
    plotitem.pcolor_cmap = geoplot.land1_colormap
    plotitem.pcolor_cmin = 0.0
    plotitem.pcolor_cmax = 2000.0
    plotitem.add_colorbar = False
    plotitem.celledges_show = 0
    plotitem.amr_patchedges_show = [0]
    #plotaxes.xlimits = [-120,-60]
    #plotaxes.ylimits = [-60,0]


    #-----------------------------------------
    # Figures for gauges
    #-----------------------------------------

    time_scale = 1./3600.
    time_label = ''
    #tlimits = [4.3,7] # hours
    tlimits = [0,6]

    plotfigure = plotdata.new_plotfigure(name='Gauges',figno=301,type='each_gauge')
    #plotfigure.kwargs = {'figsize':(8,8)}
    plotfigure.kwargs = {'figsize':(8,5)}
    # plotfigure.kwargs = {'figsize':(12,12)}
    plotfigure.clf_each_gauge = True

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    #plotaxes.axescmd = 'subplot(3,1,1)'
    plotaxes.time_scale = time_scale
    plotaxes.time_label = time_label
    plotaxes.xlimits = tlimits
    plotaxes.ylimits = 'auto'
    plotaxes.title = 'Surface elevation eta'

    def aa(current_data):
        from pylab import grid,xlabel,ylabel
        grid(True)
        xlabel('hours')
        ylabel('meters')

    plotaxes.afteraxes = aa

    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')

    # Plot eta, the amount above MHW everywhere
    def eta_wet(current_data):
        from numpy import nan, logical_and, where
        q = current_data.q
        eta = q[-1,:]
        h = q[0,:]
        return where(h>0, eta, nan)
    plotitem.plot_var = eta_wet
    plotitem.plotstyle = 'b-'


    if 0:
        # Plot h:
        plotaxes = plotfigure.new_plotaxes()
        plotaxes.axescmd = 'subplot(3,1,2)'
        plotaxes.time_scale = time_scale
        plotaxes.time_label = ''
        plotaxes.xlimits = tlimits
        plotaxes.ylimits = 'auto'
        plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
        def h(current_data):
            q = current_data.q
            h = q[0,:]
            return h
        plotitem.plot_var = h
        plotitem.plotstyle = 'b-'
    
        # Plot current speed:
        plotaxes = plotfigure.new_plotaxes()
        plotaxes.axescmd = 'subplot(3,1,3)'
        plotaxes.time_scale = time_scale
        plotaxes.time_label = ''
        plotaxes.xlimits = tlimits
        plotaxes.ylimits = 'auto'
        plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
        def speed(current_data):
            from numpy import where, sqrt
            h = current_data.q[0,:]
            h = where(h>0.01, h, 1.e6)
            u = current_data.q[1,:] / h
            v = current_data.q[2,:] / h
            s = sqrt(u**2 + v**2)
            return s
        plotitem.plot_var = speed
        plotitem.plotstyle = 'b-'
    
    
        def aa(current_data):
    
            from pylab import clf, subplot,xlabel,ylabel,title,grid,where,ylim
            q = current_data.q
            gaugeno = current_data.gaugeno
            gaugesoln = current_data.plotdata.getgauge(gaugeno)
            level = gaugesoln.level
            max_level = level.max()
            index = where(level == max_level)[0]
            hmax = q[0,index].max()
            hmin = q[0,index].min()
            etamax = q[-1,index].max()
            etamin = q[-1,index].min()
            #import pdb; pdb.set_trace()
    
            subplot(311)
            ylabel('Surface (eta=h+B), (m)')
            title('Gauge %i: Max h = %.2f, Max eta = %.2f' \
                % (gaugeno,hmax,etamax))
            grid(color='k', linestyle='dotted', linewidth=0.5)
            buffer = 0.1*(etamax - etamin)
            ylim(etamin-buffer,etamax+buffer)
    
            subplot(312)
            ylabel('h (m)')
            title('')
            grid(color='k', linestyle='dotted', linewidth=0.5)
            buffer = 0.1*(hmax - hmin)
            ylim(hmin-buffer,hmax+buffer)
    
            subplot(313)
            xlabel('time (hours)')
            ylabel('s, speed (m/s)')
            title('')
            grid(color='k', linestyle='dotted', linewidth=0.5)
    
        plotaxes.afteraxes = aa
    

    #otherfigure = plotdata.new_otherfigure(name='animations',
    #                fname='animations')

    #-------------------------------
    # Other Figures for this Site 
    #-------------------------------
    if 0:
        other_figures_dir    =  plotdata.plotdir + '/_other_figures'
        print('other_figures_dir = ',other_figures_dir)
        if os.path.isdir(other_figures_dir):
            files = os.listdir(other_figures_dir)
            print('files: ',files,' END of files')
            if len(files) > 0:
                files.sort()
                print('%i files in this directory' % len(files))
                for filename in files:
                    print('\nfilename=',filename)
                    path='_other_figures/'+filename
                    otherfigure = plotdata.new_otherfigure(name=filename,fname=path)
                    print('Added other figure: ',path)
            else:
                print('No files in this directory')
        else:
            print('*** directory not found, will not add to index')

    #-----------------------------------------
    # Figures for fgmax plots
    #-----------------------------------------
    # Note: You need to move fgmax png files into _plots/_other_figures after 
    # creating them, e.g., by running the process_fgmax notebook or script.
    # The lines below just create links to these figures from _PlotIndex.html 

    if 0:
        # included by listdir version above:
        otherfigure = plotdata.new_otherfigure(name='max depth',
                        fname='_other_figures/h_onshore.png')

        otherfigure = plotdata.new_otherfigure(name='max speed',
                        fname='_other_figures/speed.png')
            
    loc   = 'LandTrust'
    event = 'Butler6'
    fname_kmz = 'fgmax_results_%s_%s.kmz' % (loc,event)
    otherfigure = plotdata.new_otherfigure(name=fname_kmz,
                    fname='_other_figures/kmlfiles/%s' % fname_kmz)
        

    # Plots of timing (CPU and wall time):

    def make_timing_plots(plotdata):
        import os
        from clawpack.visclaw import plot_timing_stats
        try:
            timing_plotdir = plotdata.plotdir + '/timing_figures'
            os.system('mkdir -p %s' % timing_plotdir)
            units = {'comptime':'hours', 'simtime':'hours', 'cell':'billions'}
            plot_timing_stats.make_plots(outdir=plotdata.outdir, make_pngs=True,
                                          plotdir=timing_plotdir, units=units)
            os.system('cp %s/timing.* %s' % (plotdata.outdir, timing_plotdir))
        except:
            print('*** Error making timing plots')

    # create a link to this webpage from _PlotIndex.html:
    otherfigure = plotdata.new_otherfigure(name='timing',
                    fname='timing_figures/timing.html')
    otherfigure.makefig = make_timing_plots

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
    plotdata.parallel = True

    return plotdata
