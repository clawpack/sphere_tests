
""" 
Set up the plot figures, axes, and items to be done for each frame.

This module is imported by the plotting routines and then the
function setplot is called to set the plot parameters.
    
""" 

from clawpack.geoclaw import topotools
import pylab
import glob

import os

outdir2 = None
#outdir2 = os.path.abspath('../tohoku_sgn/_output_30min_afterfix')
#outdir2 = os.path.abspath('../tohoku_sgn/_output_3hrs')

dartdata = {}
for gaugeno in [21401, 21413, 21414, 21415,  21418, 21419, 51407, 52402]:
    files = glob.glob('/Users/rjl/git/tohoku2011-paper1/dart/%s*_notide.txt' % gaugeno)
    if len(files) != 1:
        print("*** Warning: found %s files for gauge number %s" \
                   % (len(files),gaugeno))
        #raise Exception("*** found %s files for gauge number %s" \
        #           % (len(files),gaugeno)   )
    try:
        fname = files[0]
        dartdata[gaugeno] = pylab.loadtxt(fname)
    except:
        pass

tlimits = {}
tlimits[21401] = [0,28800]
tlimits[21413] = [0,28800]
tlimits[21414] = [8000,28800]
tlimits[21415] = [7200,28800]
tlimits[21416] = [0,14400]
tlimits[21418] = [0,28800]
tlimits[21419] = [0,28800]
tlimits[51407] = [8000,28800]
tlimits[52402] = [8000,28800]

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

    plotdata.format = 'ascii'


    # To plot gauge locations on pcolor or contour plot, use this as
    # an afteraxis function:

    def addgauges(current_data):
        from clawpack.visclaw import gaugetools
        gaugetools.plot_gauge_locations(current_data.plotdata, \
             gaugenos='all', format_string='ko', add_labels=True)

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
    # Figure for pcolor plot
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='full domain', figno=0)
    plotfigure.kwargs = {'facecolor':'w'}

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes('pcolor')
    plotaxes.title = 'Surface'
    plotaxes.scaled = True

    def fixup(current_data):
        import pylab
        #addgauges(current_data)
        t = current_data.t
        t = t / 3600.  # hours
        pylab.title('Surface at %4.2f hours' % t, fontsize=15)
        pylab.xticks(fontsize=12)
        pylab.yticks(fontsize=12)
        #pylab.plot([205],[19.7],'wo',markersize=10)
        #pylab.text(200,22,'Hilo',color='k',fontsize=25)
        #pylab.plot([139.7],[35.6],'yo',markersize=5)
        #pylab.text(133.3,36.5,'Sendai',color='y',fontsize=15)
        #addgauges(current_data)

    plotaxes.afteraxes = fixup

    # Water
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    #plotitem.plot_var = geoplot.surface
    plotitem.plot_var = geoplot.surface_or_depth
    plotitem.pcolor_cmap = geoplot.tsunami_colormap
    plotitem.pcolor_cmin = -0.5
    plotitem.pcolor_cmax = 0.5
    plotitem.add_colorbar = True
    plotitem.colorbar_shrink = 0.5
    plotitem.colorbar_kwargs = {'extend':'both'}
    plotitem.amr_patchedges_show = [0] #[0,0,1,1,1]
    plotitem.amr_patchedges_color = ['k','k','k','g','y']

    # Land
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    plotitem.plot_var = geoplot.land
    plotitem.pcolor_cmap = geoplot.land_colors
    plotitem.pcolor_cmin = 0.0
    plotitem.pcolor_cmax = 100.0
    plotitem.add_colorbar = False
    #plotaxes.xlimits = [138,155]
    #plotaxes.ylimits = [25,42]



    #-----------------------------------------
    # Figure for zoom plot
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='Zoom', figno=1)
    plotfigure.show = False

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes('pcolor')
    plotaxes.title = 'Surface'
    plotaxes.scaled = True
    plotaxes.xlimits = [140,146]
    plotaxes.ylimits = [35,41]


    # Water
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    #plotitem.plot_var = geoplot.surface
    plotitem.plot_var = geoplot.surface_or_depth
    plotitem.pcolor_cmap = colormaps.blue_white_red
    plotitem.pcolor_cmin = -10.0
    plotitem.pcolor_cmax = 10.0
    plotitem.add_colorbar = True

    # Land
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    plotitem.plot_var = geoplot.land
    plotitem.pcolor_cmap = geoplot.land_colors
    plotitem.pcolor_cmin = 0.0
    plotitem.pcolor_cmax = 100.0
    plotitem.add_colorbar = False


    plotitem = plotaxes.new_plotitem(plot_type='2d_contour')
    #plotitem.show = False
    plotitem.plot_var = geoplot.surface
    plotitem.contour_levels = linspace(-13,13,14)
    plotitem.amr_contour_colors = ['k']  # color on each level
    #plotitem.kwargs = {'linestyles':'solid','linewidths':2}
    plotitem.amr_contour_show = [0,0,0,1]  


    #-----------------------------------------
    # Figure for surface with transect too
    #-----------------------------------------
    

    #x1trans, x2trans = 141, 147.  # xg1 = 145.5
    #y1trans, y2trans = 37.4, 37.867  # yg1 = 37.6
    
    if 0:
        x1trans, x2trans = 141, 148.
        y1trans, y2trans = 37.4, 37.4
        xlimits = [140,148]
        ylimits = [35,39]
        
    if 1:
        x1trans, x2trans = 140, 170.
        y1trans, y2trans = 37.4, 28.
        xlimits = [140,180]
        ylimits = [15,39]
        
    xtrans = linspace(x1trans, x2trans, 1000)
    ytrans = linspace(y1trans, y2trans, 1000)
    
    #eta_limits = (-2,2)
    eta_limits = (-10,10)

    
    plotfigure = plotdata.new_plotfigure(name='Surface w/transect', figno=20)
    plotfigure.show = False
    if outdir2:
        plotfigure.kwargs = {'figsize': (12,8)}
    else:
        plotfigure.kwargs = {'figsize': (8,8)}

    # Axes for surface:
    plotaxes = plotfigure.new_plotaxes('pcolor')
    plotaxes.axescmd = 'axes([.15,.5,.8,.45])'
    plotaxes.title = 'Surface'
    plotaxes.xlimits = xlimits
    plotaxes.ylimits = ylimits
    
    def fixup_wtransect(current_data):
        import pylab
        #addgauges(current_data)
        background_image2(current_data)
        title_hours(current_data)
        t = current_data.t
        timestr = timeformat(t)
        pylab.title('%s at %s' % (label1,timestr))
        pylab.xticks(fontsize=8)
        pylab.yticks(fontsize=8)
        pylab.gca().set_aspect(1/pylab.cos(30*pylab.pi/180))
        pylab.plot([x1trans,x2trans], [y1trans,y2trans], 'k--', linewidth=0.7)
        #pylab.text(-20, 29.4, 'Transect', fontsize=10, color='k')
    plotaxes.afteraxes = fixup_wtransect

    # Water
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    #plotitem.plot_var = surface_or_depth  # local version
    plotitem.plot_var = geoplot.surface_or_depth
    plotitem.pcolor_cmap = geoplot.tsunami_colormap

    #plotitem.pcolor_cmin = -2.
    #plotitem.pcolor_cmax = 2.
    plotitem.pcolor_cmin = -2.
    plotitem.pcolor_cmax = 2.

    plotitem.add_colorbar = True
    plotitem.colorbar_shrink = 0.5
    plotitem.colorbar_kwargs = {'extend':'both'}

    # Land
    plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
    plotitem.plot_var = geoplot.land
    plotitem.pcolor_cmap = geoplot.land_colors
    plotitem.pcolor_cmin = 0.0
    plotitem.pcolor_cmax = 20.0
    plotitem.add_colorbar = False
    plotitem.amr_celledges_show = [0,0,0]
    plotitem.patchedges_show = 0

    # add contour lines of bathy if desired:
    plotitem = plotaxes.new_plotitem(plot_type='2d_contour')
    plotitem.show = False
    plotitem.plot_var = geoplot.topo
    plotitem.contour_levels = [0]  #linspace(-3000,-3000,1)
    plotitem.amr_contour_colors = ['g']  # color on each level
    plotitem.kwargs = {'linestyles':'solid','linewidths':1.}
    plotitem.amr_contour_show = [0,0,1]  
    plotitem.celledges_show = 0
    plotitem.patchedges_show = 0

    if outdir2 is not None:
        # make the axes above smaller
        plotaxes.axescmd = 'axes([.1,.5,.4,.45])'
        
        # add another axes for the other results from outdir2:
        plotaxes = plotfigure.new_plotaxes('pcolor2')
        plotaxes.axescmd = 'axes([.55,.5,.4,.45])'
        plotaxes.title = 'outdir2'
        plotaxes.xlimits = xlimits
        plotaxes.ylimits = ylimits
        
        def fixup_wtransect(current_data):
            import pylab
            #addgauges(current_data)
            background_image2(current_data)
            title_hours(current_data)
            t = current_data.t
            timestr = timeformat(t)
            pylab.title('%s at %s' % (label2,timestr))
            pylab.xticks(fontsize=8)
            pylab.yticks(fontsize=8)
            pylab.gca().set_aspect(1/pylab.cos(30*pylab.pi/180))
            pylab.plot([x1trans,x2trans], [y1trans,y2trans], 'k--', linewidth=0.7)
            #pylab.text(-73, 39, 'Transect', fontsize=7, color='k')
            
        plotaxes.afteraxes = fixup_wtransect

        # Water
        plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
        plotitem.outdir = outdir2
        plotitem.plot_var = surface_or_depth  # local version
        #plotitem.plot_var = geoplot.surface_or_depth
        plotitem.pcolor_cmap = geoplot.tsunami_colormap
        plotitem.pcolor_cmin = -2.
        plotitem.pcolor_cmax = 2.
        plotitem.add_colorbar = True
        plotitem.colorbar_shrink = 0.5
        plotitem.colorbar_kwargs = {'extend':'both'}

        # Land
        plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
        plotitem.outdir = outdir2
        plotitem.plot_var = geoplot.land
        plotitem.pcolor_cmap = geoplot.land_colors
        plotitem.pcolor_cmin = 0.0
        plotitem.pcolor_cmax = 50.0
        plotitem.add_colorbar = False
        plotitem.amr_celledges_show = [0,0,0]
        plotitem.patchedges_show = 0

        # add contour lines of bathy if desired:
        plotitem = plotaxes.new_plotitem(plot_type='2d_contour')
        #plotitem.show = False
        plotitem.outdir = outdir2
        plotitem.plot_var = geoplot.topo
        plotitem.contour_levels = [0]  #linspace(-3000,-3000,1)
        plotitem.amr_contour_colors = ['g']  # color on each level
        plotitem.kwargs = {'linestyles':'solid','linewidths':0.5}
        plotitem.amr_contour_show = [0,0,1]  
        plotitem.celledges_show = 0
        plotitem.patchedges_show = 0
    
    
    #-----------------------------------------
    # Axes for transect
    #-----------------------------------------

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes('transect')
    plotaxes.axescmd = 'axes([.1,.1,.8,.3])'

    def plot_xsec(current_data):
        from pylab import plot,legend,xlabel,grid,xlim,ylim,title,fill_between
        from numpy import cos,pi,linspace,zeros,ones,hstack,sqrt,nan,where,nanmax
        from clawpack.pyclaw import Solution
        pd = current_data.plotdata
        frameno = current_data.frameno
        framesoln = Solution(frameno, path=pd.outdir, file_format=pd.format)
        eta_trans = gridtools.grid_output_2d(framesoln, -1, xtrans, ytrans)
        h_trans = gridtools.grid_output_2d(framesoln, 0, xtrans, ytrans)
        B_trans = eta_trans - h_trans
        eta_wet = where(h_trans>0, eta_trans, nan)
        fill_color = [0.5, 0.5, 1]
        #fill_between(xtrans, B_trans, eta_wet, color=fill_color)
        plot(xtrans, eta_wet, 'b', label=label1)

        
        if outdir2 is not None:
            framesoln = Solution(frameno, path=outdir2, file_format=pd.format)
            eta_trans = gridtools.grid_output_2d(framesoln, -1, xtrans, ytrans)
            h_trans = gridtools.grid_output_2d(framesoln, 0, xtrans, ytrans)
            B_trans = eta_trans - h_trans
            eta_wet = where(h_trans>0, eta_trans, nan)
            fill_color = [0.7, 0.4, 1, 0.5]
            #fill_between(xtrans, B_trans, eta_wet, color=fill_color)
            plot(xtrans, eta_wet, 'm', label=label2)
            #plot(xtrans, B_trans, 'g', label='topography')
            
        #xlabel('distance')
        title('Along transect')  
        fill_color = [0.6, 1, 0.6]
        fill_between(xtrans, B_trans, -10000, color=fill_color)
        plot(xtrans, B_trans, 'g', label='topography')
        xlabel('longitude along transect')
        xlim(x1trans,x2trans)
        #ymax = max(100, nanmax(eta_wet)+10)  # show full wave at early times
        #ymax = 20
        #ylim(-10,ymax)
        ylim(eta_limits)
        #ylim(-3000,2000)
        lloc = 'upper left'
        if 0 and current_data.t < 241:
            title('Along transect (zoom near crater)')  
            xlim(-22,-21)
            ylim(-6000,2500)
            lloc = 'upper right'
        grid(True)

        legend(loc=lloc,framealpha=1,fontsize=8)

    plotaxes.afteraxes = plot_xsec



    #-----------------------------------------
    # Figures for gauges
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='Surface & topo', figno=300, \
                    type='each_gauge')
    plotfigure.clf_each_gauge = True

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.time_scale = 1/3600. # convert to hours
    plotaxes.xlimits = 'auto'
    plotaxes.ylimits = 'auto'
    plotaxes.title = 'Surface'

    # Plot surface as blue curve:
    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    plotitem.plot_var = 3
    plotitem.plotstyle = 'b-'
    plotitem.kwargs = {'linewidth':2}

    # Plot comparison as red curve:
    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    plotitem.show = (outdir2 is not None)
    plotitem.outdir = outdir2
    plotitem.plot_var = 3
    plotitem.plotstyle = 'r-'
    plotitem.kwargs = {'linewidth':2}

    # Plot topo as green curve:
    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    plotitem.show = False

    def gaugetopo(current_data):
        q = current_data.q
        h = q[:,0]
        eta = q[:,3]
        topo = eta - h
        return topo
        
    plotitem.plot_var = gaugetopo
    plotitem.plotstyle = 'g-'

    def add_zeroline(current_data):
        from pylab import plot, legend, xticks, floor
        t = current_data.t
        #legend(('surface','topography'),loc='lower left')
        plot([0,10],[0,0],'k')
        #n = int(floor(t.max()/3600.)) + 2
        #xticks([3600*i for i in range(n)])

    def plot_dart(current_data):
        import pylab
        gaugeno = current_data.gaugeno
        try:
            dart = dartdata[gaugeno]
            pylab.plot(dart[:,0]/3600.,dart[:,1],'k')
            if outdir2 is None:
                pylab.legend(['SWE','DART data'])
            else:
                pylab.legend(['SWE','SGN','DART data'])
        except:
            if outdir2 is None:
                pylab.legend(['SWE'])
            else:
                pylab.legend(['SWE','SGN'])
        add_zeroline(current_data)
        try:
            pass
            #pylab.xlim(tlimits[gaugeno])
        except:
            pass


    plotaxes.afteraxes = plot_dart



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

    return plotdata
