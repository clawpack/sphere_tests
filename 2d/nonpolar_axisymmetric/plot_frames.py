"""
Make plots for the paper.
Note that figno=120 is used, as specified in setplot.py
and the xlimits,ylimits for the specific frames used here are set there.
The savefig to a pdf file is also done in setplot.
"""

from pylab import *
import setplot

plotdata = setplot.setplot()

plotdata.printfigs = False
plotdata.print_fignos = [0,1]

plotdata.outdir = '_output_sphere0'
plotdata.plotframe(5)
figure(0)
fname = 'nonpolar_sphere0.png'
savefig(fname, bbox_inches='tight')
print('Created ',fname)
figure(1)
fname = 'nonpolar_sphere0r.png'
savefig(fname, bbox_inches='tight')
print('Created ',fname)

plotdata.outdir = '_output_sphere2'
plotdata.plotframe(5)
figure(0)
fname = 'nonpolar_sphere2.png'
savefig(fname, bbox_inches='tight')
print('Created ',fname)
figure(1)
fname = 'nonpolar_sphere2r.png'
savefig(fname, bbox_inches='tight')
print('Created ',fname)

plotdata.outdir = '_output_sphere2'
plotdata.plotframe(0)
figure(0)
fname = 'nonpolar_t0.png'
savefig(fname, bbox_inches='tight')
print('Created ',fname)
figure(1)
fname = 'nonpolar_t0r.png'
savefig(fname, bbox_inches='tight')
print('Created ',fname)

if 0:
    # For later times,
    # reset plotitems in pcolor plot so coarser grids aren't shown near shore:
    plotfigure = plotdata.plotfigure_dict['For paper']
    plotaxes = plotfigure.plotaxes_dict['pcolor']
    for plotitem in plotaxes.plotitem_dict.values():
        plotitem.amr_data_show = [0,0,1,1]
        
    for frameno in [21,23,26]:
        plotdata.plotframe(frameno)
