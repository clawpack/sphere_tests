
from pylab import *
from clawpack.pyclaw import Solution
from clawpack.geoclaw import topotools
from clawpack.visclaw import gaugetools, plottools, colormaps, gridtools
from clawpack.visclaw import legend_tools
import os

#x1trans,x2trans = -168, -156.4
#y1trans,y2trans = 51, 21
x1trans,x2trans = -168, -150.
y1trans,y2trans = 51, 12

xtrans = linspace(x1trans,x2trans,1000)
ytrans = linspace(y1trans,y2trans,1000)

def plot_transect(frameno, outdir, clear=True, color='b'):
    framesoln = Solution(frameno, path=outdir, file_format='binary')
    eta_trans = gridtools.grid_output_2d(framesoln, -1, xtrans, ytrans)
    #h_trans = gridtools.grid_output_2d(framesoln, 0, xtrans, ytrans)
    figure(51, figsize=(9,6))
    if clear: clf()
    plot(ytrans, eta_trans, color)
    title('Surface eta along transect')
    xlabel('latitude along transect')
    xlim(y1trans,y2trans)
    grid(True)


def compare():
    close(51)
    for frameno in range(2,9):
        P.plot_transect(frameno,'_output_nosphere',False, 'b')

    for frameno in range(2,9):
        P.plot_transect(frameno,'_output_sphere',False, 'r')

def compare2():
    close(51)
    for frameno in range(1,6):
        plot_transect(frameno,'_output_nosphere_6hr',False,'b')
    for frameno in range(1,6):
        plot_transect(frameno,'_output_sphere_6hr',False,'r')
    title('Surface eta along transect at 1,2,3,4,5 hours',fontsize=15)
    xlabel('latitude along transect',fontsize=12)
    ylabel('meters',fontsize=12)
    xlim(51,15)
    legend_tools.add_legend(['Without source terms','With source terms'],
            ['b','r'],loc='upper right',framealpha=1,fontsize=12)
    savefig('butler_transect_5hrs.pdf', bbox_inches='tight')

