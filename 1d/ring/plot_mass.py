
from pylab import *

mass1 = loadtxt('_output_nosphere/total_zeta_mass.txt')
mass2 = loadtxt('_output_sphere/total_zeta_mass.txt')

figure(3,figsize=(9,5))
clf()
m0 = 0.786581E+14
semilogy(mass1[2:,0]/3600.,abs(mass1[2:,2]/m0),'b',linewidth=2,
         label='no source term')
semilogy(mass2[2:,0]/3600.,abs(mass2[2:,2]/m0),'r',linewidth=2,
         label='with source term')
legend(loc='lower right',framealpha=1,fontsize=12)
ylim(1e-7,1)
grid(True)
title('Relative change in total mass',fontsize=15)
xlabel('Hours', fontsize=12)

savefig('mass1d.pdf', bbox_inches='tight')

