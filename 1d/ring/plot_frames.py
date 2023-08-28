

from pylab import *
import setplot

plotdata = setplot.setplot()

plotdata.printfigs = False
plotdata.print_fignos = [1]

case = 'sphere'
plotdata.outdir = '_output_%s' % case

for frameno in [0,4,8,10,12,14]:
    plotdata.plotframe(frameno)
    fname = '%s_1d_frame%s.pdf' % (case,str(frameno).zfill(2))
    savefig(fname, bbox_inches='tight')
    print('Created ',fname)
