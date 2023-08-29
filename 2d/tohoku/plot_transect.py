
from pylab import *
from clawpack.pyclaw import Solution
from clawpack.geoclaw import topotools
from clawpack.visclaw import gaugetools, plottools, colormaps, gridtools
from clawpack.visclaw import legend_tools
import os

#x1trans,x2trans = -168, -156.4
#y1trans,y2trans = 51, 21
#x1trans,x2trans = 145, 200
#y1trans,y2trans = 35,25
x1trans,x2trans = 145, 210
y1trans,y2trans = 35,20

xtrans = linspace(x1trans,x2trans,1000)
ytrans = linspace(y1trans,y2trans,1000)

def plot_transect(frameno, outdir, clear=True, color='b'):
    framesoln = Solution(frameno, path=outdir, file_format='binary')
    eta_trans = gridtools.grid_output_2d(framesoln, -1, xtrans, ytrans)
    h_trans = gridtools.grid_output_2d(framesoln, 0, xtrans, ytrans)
    eta_trans = where(h_trans > 0.01, eta_trans, nan)
    figure(51, figsize=(9,6))
    if clear: clf()
    plot(xtrans, eta_trans, color)
    title('Surface eta along transect')
    xlabel('longatude along transect')
    xlim(x1trans,x2trans)
    grid(True)


def compare():
    close(51)
    for frameno in range(2,9):
        P.plot_transect(frameno,'_output_nosphere',False, 'b')

    for frameno in range(2,9):
        P.plot_transect(frameno,'_output_sphere',False, 'r')

def compare2():
    close(51)
    for frameno in range(1,9):
        plot_transect(frameno,'_output_nosphere',False,'b')
    for frameno in range(1,9):
        plot_transect(frameno,'_output_sphere',False,'r')
    title('Surface eta along transect at 1,2,...,8 hours',fontsize=15)
    xlabel('longitude along transect',fontsize=12)
    ylabel('meters',fontsize=12)
    xlim(145,210)
    legend_tools.add_legend(['Without source terms','With source terms'],
            ['b','r'],loc='upper right',framealpha=1,fontsize=12)
    savefig('tohoku_transect_8hrs.pdf', bbox_inches='tight')

if __name__=='__main__':
    compare2()
