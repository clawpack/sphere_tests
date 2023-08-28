
from pylab import *

lines = open('_output_nosphere/zeta.txt').readlines()
mass1 = empty((len(lines),2))
for i,line in enumerate(lines):
    tokens = line.split()
    t = float(tokens[3].replace(',',''))
    dm = float(tokens[-1])
    mass1[i,:] = t,dm

lines = open('_output_sphere/zeta.txt').readlines()
mass2 = empty((len(lines),2))
for i,line in enumerate(lines):
    tokens = line.split()
    t = float(tokens[3].replace(',',''))
    dm = float(tokens[-1])
    if t <= 5*3600:
        mass2[i,:] = t,dm
    else:
        mass2[i,:] = nan,nan

figure(3,figsize=(9,5))
clf()
m0 = 0.484246850749566E+15 #0.786581E+14
semilogy(mass1[2:,0]/3600.,abs(mass1[2:,1]/m0),'b',linewidth=2,
         label='no source term')
semilogy(mass2[2:,0]/3600.,abs(mass2[2:,1]/m0),'r',linewidth=2,
         label='with source term')
legend(loc='lower right',framealpha=1,fontsize=12)
ylim(1e-7,1)
grid(True)
title('Relative change in total mass',fontsize=15)
xlabel('Hours', fontsize=12)

savefig('mass2d.pdf', bbox_inches='tight')

