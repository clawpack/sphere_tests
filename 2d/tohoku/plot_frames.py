

from pylab import *
import setplot

plotdata = setplot.setplot()

plotdata.printfigs = False
plotdata.print_fignos = [0]

plotdata.outdir = '_output_sphere'

#x1trans,x2trans = 145, 200
#y1trans,y2trans = 35,25
x1trans,x2trans = 145, 210
y1trans,y2trans = 35,20

#for hour in [2,4,6]:
for hour in range(9):
    plotdata.plotframe(hour)
    plot([x1trans,x2trans],[y1trans,y2trans],'k',linewidth=0.7)
    fname = 'tohoku_sphere_%hr.pdf' % hour
    savefig(fname, bbox_inches='tight')
    print('Created ',fname)
