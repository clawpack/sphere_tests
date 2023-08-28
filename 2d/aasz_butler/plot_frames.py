

from pylab import *
import setplot

plotdata = setplot.setplot()

plotdata.printfigs = False
plotdata.print_fignos = [21]

plotdata.outdir = '_output_nosphere_6hr'

for hour in [1,3,5]:
    plotdata.plotframe(hour)
    plot([-168, -150.],[51, 12],'k',linewidth=0.7)
    fname = 'butler_nosphere_%hr.pdf' % hour
    savefig(fname, bbox_inches='tight')
    print('Created ',fname)
