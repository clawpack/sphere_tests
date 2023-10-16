"""
Module to set up run time parameters for Clawpack.

The values set in the function setrun are then written out to data files
that will be read in by the Fortran code.

"""


import os
import numpy as np
from clawpack.amrclaw.data import FlagRegion
from clawpack.geoclaw import fgmax_tools
#from clawpack.geoclaw import fgout_tools

try:
    CLAW = os.environ['CLAW']
except:
    raise Exception("*** Must first set CLAW enviornment variable")


rundir = os.getcwd()
print('rundir = %s' % rundir)



# set topodir and dtopodir to directory where topo and dtopo files are found:
hawaii = '/Users/rjl/git/hawaii_land_trust/'
topodir = hawaii + '/topo/topofiles'
dtopodir = hawaii + '/dtopo/dtopofiles'

#------------------------------
def setrun(claw_pkg='geoclaw'):
#------------------------------

    """
    Define the parameters used for running Clawpack.

    INPUT:
        claw_pkg expected to be "geoclaw" for this setrun.

    OUTPUT:
        rundata - object of class ClawRunData

    """

    from clawpack.clawutil import data

    assert claw_pkg.lower() == 'geoclaw',  "Expected claw_pkg = 'geoclaw'"

    num_dim = 2
    rundata = data.ClawRunData(claw_pkg, num_dim)


    #------------------------------------------------------------------
    # Problem-specific parameters to be written to setprob.data:
    #------------------------------------------------------------------
    
    #probdata = rundata.new_UserData(name='probdata',fname='setprob.data')

    #------------------------------------------------------------------
    # GeoClaw specific parameters:
    #------------------------------------------------------------------
    try:
        geo_data = rundata.geo_data
    except:
        print("*** Error, this rundata has no geo_data attribute")
        raise AttributeError("Missing geo_data attribute")

    #------------------------------------------------------------------
    # Standard Clawpack parameters to be written to claw.data:
    #   (or to amr2ez.data for AMR)
    #------------------------------------------------------------------
    clawdata = rundata.clawdata  # initialized when rundata instantiated


    # Set single grid parameters first.
    # See below for AMR parameters.


    # ---------------
    # Spatial domain:
    # ---------------

    # Number of space dimensions:
    clawdata.num_dim = num_dim

    # Lower and upper edge of computational domain:

    # shift so that cell centers on finest grid align with DEM:

    sec16 = 1./(6*3600.)  # one sixth arcsecond

    #etopo1 was -180,-110,11,63 and -200,-180,11,63
    clawdata.lower[0] = -199. - sec16       # west longitude
    clawdata.upper[0] = -110. - sec16       # east longitude
    clawdata.lower[1] = 12. - sec16         # south latitude
    clawdata.upper[1] = 63. - sec16         # north latitude

    #coarest grid is one degree
    clawdata.num_cells[0] = 89
    clawdata.num_cells[1] = 51


    # ---------------
    # Size of system:
    # ---------------

    # Number of equations in the system:
    clawdata.num_eqn = 3

    # Number of auxiliary variables in the aux array (initialized in setaux)
    clawdata.num_aux = 3

    # Index of aux array corresponding to capacity function, if there is one:
    clawdata.capa_index = 2

    
    
    # -------------
    # Initial time:
    # -------------

    clawdata.t0 = 0.0


    # Restart from checkpoint file of a previous run?
    # If restarting, t0 above should be from original run, and the
    # restart_file 'fort.chkNNNNN' specified below should be in 
    # the OUTDIR indicated in Makefile.

    clawdata.restart = False         # True to restart from prior results
    clawdata.restart_file = ''

    tstart_finestgrid = 3600*4.25     #4.25 hours

    # -------------
    # Output times:
    #--------------

    # Specify at what times the results should be written to fort.q files.
    # Note that the time integration stops after the final output time.
    # The solution at initial time t0 is always written in addition.

    clawdata.output_style = 1

    ########  Start with a one half hour run, probably enough time to destination
    if clawdata.output_style==1:
        # Output nout frames at equally spaced times up to tfinal:
        ## ADJUST:
        clawdata.num_output_times = 6
        clawdata.tfinal = 6*3600
        clawdata.output_t0 = True  # output at initial (or restart) time?

    elif clawdata.output_style == 2:
        # Specify a list of output times.
        min5 = 300
        min15 = 900
        hour=3600
        #clawdata.output_times = [2*min5,4*min5,6*min5,8*min5,10*min5,12*min5]  #a one hour run
        #clawdata.output_times = []  #a six hour run, outputting every 15 minutes
        #for jtime in range(1*hour,6*hour+min15,min15):
        #   clawdata.output_times.append(jtime)
        clawdata.output_times = np.arange(5*3600., 7.1*3600., 600.)
        

    elif clawdata.output_style == 3:
        # Output every iout timesteps with a total of ntot time steps:
        clawdata.output_step_interval = 1
        clawdata.total_steps = 1
        clawdata.output_t0 = True
        

    clawdata.output_format = 'binary'

    clawdata.output_q_components = 'all'   # need all
    clawdata.output_aux_components = 'none'  # eta=h+B is in q
    clawdata.output_aux_onlyonce = False    # output aux arrays each frame



    # ---------------------------------------------------
    # Verbosity of messages to screen during integration:
    # ---------------------------------------------------

    # The current t, dt, and cfl will be printed every time step
    # at AMR levels <= verbosity.  Set verbosity = 0 for no printing.
    #   (E.g. verbosity == 2 means print only on levels 1 and 2.)
    clawdata.verbosity = 1



    # --------------
    # Time stepping:
    # --------------

    # if dt_variable==1: variable time steps used based on cfl_desired,
    # if dt_variable==0: fixed time steps dt = dt_initial will always be used.
    clawdata.dt_variable = True

    # Initial time step for variable dt.
    # If dt_variable==0 then dt=dt_initial for all steps:
    clawdata.dt_initial = 0.2

    # Max time step to be allowed if variable dt used:
    clawdata.dt_max = 1e+99

    # Desired Courant number if variable dt used, and max to allow without
    # retaking step with a smaller dt:
    clawdata.cfl_desired = 0.75
    clawdata.cfl_max = 1.0

    # Maximum number of time steps to allow between output times:
    clawdata.steps_max = 5000




    # ------------------
    # Method to be used:
    # ------------------

    # Order of accuracy:  1 => Godunov,  2 => Lax-Wendroff plus limiters
    clawdata.order = 2
    
    # Use dimensional splitting? (not yet available for AMR)
    clawdata.dimensional_split = 'unsplit'
    
    # For unsplit method, transverse_waves can be 
    #  0 or 'none'      ==> donor cell (only normal solver used)
    #  1 or 'increment' ==> corner transport of waves
    #  2 or 'all'       ==> corner transport of 2nd order corrections too
    clawdata.transverse_waves = 2

    # Number of waves in the Riemann solution:
    clawdata.num_waves = 3
    
    # List of limiters to use for each wave family:  
    # Required:  len(limiter) == num_waves
    # Some options:
    #   0 or 'none'     ==> no limiter (Lax-Wendroff)
    #   1 or 'minmod'   ==> minmod
    #   2 or 'superbee' ==> superbee
    #   3 or 'mc'       ==> MC limiter
    #   4 or 'vanleer'  ==> van Leer
    clawdata.limiter = ['mc', 'mc', 'mc']

    clawdata.use_fwaves = True    # True ==> use f-wave version of algorithms
    
    # Source terms splitting:
    #   src_split == 0 or 'none'    ==> no source term (src routine never called)
    #   src_split == 1 or 'godunov' ==> Godunov (1st order) splitting used, 
    #   src_split == 2 or 'strang'  ==> Strang (2nd order) splitting used,  not recommended.
    clawdata.source_split = 'godunov'


    # --------------------
    # Boundary conditions:
    # --------------------

    # Number of ghost cells (usually 2)
    clawdata.num_ghost = 2

    # Choice of BCs at xlower and xupper:
    #   0 => user specified (must modify bcN.f to use this option)
    #   1 => extrapolation (non-reflecting outflow)
    #   2 => periodic (must specify this at both boundaries)
    #   3 => solid wall for systems where q(2) is normal velocity

    clawdata.bc_lower[0] = 'extrap'
    clawdata.bc_upper[0] = 'extrap'

    clawdata.bc_lower[1] = 'extrap'
    clawdata.bc_upper[1] = 'extrap'



    # --------------
    # Checkpointing:
    # --------------

    # Specify when checkpoint files should be created that can be
    # used to restart a computation.

    # negative checkpoint_style means alternate between aaaaa and bbbbb files
    # so that at most 2 checkpoint files exist at any time, useful when
    # doing frequent checkpoints of large problems.

    clawdata.checkpt_style = -2

    if clawdata.checkpt_style == 0:
        # Do not checkpoint at all
        pass

    elif clawdata.checkpt_style == 1:
        # Checkpoint only at tfinal.
        pass

    elif abs(clawdata.checkpt_style) == 2:
        # Specify a list of checkpoint times.  
        clawdata.checkpt_times = 3600.*np.arange(1,16,1)

    elif abs(clawdata.checkpt_style) == 3:
        # Checkpoint every checkpt_interval timesteps (on Level 1)
        # and at the final time.
        clawdata.checkpt_interval = 5


    # ---------------
    # AMR parameters:
    # ---------------
    amrdata = rundata.amrdata

    # max number of refinement levels:
    amrdata.amr_levels_max = 3  #8

    # List of refinement ratios at each level (length at least mxnest-1)

    # dx = dy = 1deg, 4', 1', 30", 6", 2", 1", 1/3"":
    amrdata.refinement_ratios_x = [15,4,2,5,3,2,3]
    amrdata.refinement_ratios_y = [15,4,2,5,3,2,3]
    amrdata.refinement_ratios_t = [15,4,2,5,3,2,3]

    # Specify type of each aux variable in amrdata.auxtype.
    # This must be a list of length maux, each element of which is one of:
    #   'center',  'capacity', 'xleft', or 'yleft'  (see documentation).

    amrdata.aux_type = ['center','capacity','yleft']


    # Flag using refinement routine flag2refine rather than richardson error
    amrdata.flag_richardson = False    # use Richardson?
    amrdata.flag2refine = True

    # steps to take on each level L between regriddings of level L+1:
    amrdata.regrid_interval = 3

    # width of buffer zone around flagged points:
    # (typically the same as regrid_interval so waves don't escape):
    amrdata.regrid_buffer_width  = 2

    # clustering alg. cutoff for (# flagged pts) / (total # of cells refined)
    # (closer to 1.0 => more small grids may be needed to cover flagged cells)
    amrdata.clustering_cutoff = 0.700000

    # print info about each regridding up to this level:
    amrdata.verbosity_regrid = 0  

       
    # == Physics ==
    geo_data.gravity = 9.81
    geo_data.coordinate_system = 2
    geo_data.sphere_source = 2
    geo_data.earth_radius = 6367.5e3

    # == Forcing Options
    geo_data.coriolis_forcing = False

    # == Algorithm and Initial Conditions ==
    geo_data.sea_level = 0.0
    geo_data.dry_tolerance = 1.e-3
    geo_data.friction_forcing = True
    geo_data.manning_coefficient =.025
    geo_data.friction_depth = 1e6

    # Refinement settings
    refinement_data = rundata.refinement_data
    refinement_data.variable_dt_refinement_ratios = True
    refinement_data.wave_tolerance = 0.02

    # == settopo.data values ==
    topo_data = rundata.topo_data
    # for topography, append lines of the form
    #    [topotype, minlevel, maxlevel, t1, t2, fname]

    #topodir = '/Users/rjl/topo/topofiles'
    topofiles = topo_data.topofiles

    # 1-minute topo:
    topofiles.append([3, topodir + '/etopo1_-180_-110_11_63_1min.asc'])
    topofiles.append([3, topodir + '/etopo1_-200_-180_11_63_1min.asc'])

    #36-second topo:
    #topofiles.append([3, topodir + '/hawaii_36s.asc'])

    #6-second topo:
    topofiles.append([3, topodir + '/hawaii_6s.txt'])

    # 3-second topo:
    #topofiles.append([3, topodir + '/nw_pacific_3sec_cropped.asc'])

    if 0:
        # 2 arcsecond topo:
        topofiles.append([3, topodir + '/topo_waihee_W_2s.asc'])
        topofiles.append([3, topodir + '/topo_waihee_E_2s.asc'])

        # 1/3 arcsecond topo:
        topofiles.append([3, topodir + '/topo_waihee_W_13s.asc'])
        topofiles.append([3, topodir + '/topo_waihee_E_13s.asc'])


    if 1:

        # 2 second topo around Hilo:
        topofiles.append([3, topodir + '/ncei19_n19x75_w155x00_2021v1_2s.asc'])
        topofiles.append([3, topodir + '/ncei19_n19x75_w155x25_2021v1_2s.asc'])
        topofiles.append([3, topodir + '/ncei19_n20x00_w155x25_2021v1_2s.asc'])

        # 1/3 second topo around Hilo:
        topofiles.append([3, topodir + '/topo_hilo_13s.asc'])
        topofiles.append([3, topodir + '/topo_hiloN_13s.asc'])

    # == setdtopo.data values ==
    dtopo_data = rundata.dtopo_data
    # for moving topography, append lines of the form :   (<= 1 allowed for now!)
    #   [topotype, fname]

    dtopo_data.dtopofiles = [[3, dtopodir + '/Butler6.tt3']]
    #dtopo_data.dtopofiles = [[3, dtopodir + '/okal1946a.tt3']]
    #dtopo_data.dtopofiles = [[3, dtopodir + '/butler1946a.tt3']]

    dtopo_data.dt_max_dtopo = 0.2


    # == setqinit.data values ==
    rundata.qinit_data.qinit_type = 0
    rundata.qinit_data.qinitfiles = []
    # for qinit perturbations, append lines of the form: (<= 1 allowed for now!)
    #   [minlev, maxlev, fname]

    #rundata.qinit_data.variable_eta_init = True  # for subsidence
    rundata.qinit_data.variable_eta_init = False  # for subsidence


    # ---------------
    # Regions:
    # ---------------
    rundata.regiondata.regions = []
    # to specify regions of refinement append lines of the form
    #  [minlevel,maxlevel,t1,t2,x1,x2,y1,y2]

    flagregions = rundata.flagregiondata.flagregions  # initialized to []
    
    # dx = dy = 1deg, 4', 1', 30", 6", 2", 1", 1/3"":
    
    # Computational domain Variable Region - 1degree to 4min to 1min:
    # Level 3 below is 1 min
    # Note that this is a rectangle specified in the new way
    # (other regions below will force/allow more refinement)
    flagregion = FlagRegion(num_dim=2)
    flagregion.name = 'Region_domain_firsthour'
    flagregion.minlevel = 1
    flagregion.maxlevel = 3
    flagregion.t1 = 0.
    flagregion.t2 = 1*3600.
    flagregion.spatial_region_type = 1  # Rectangle
    flagregion.spatial_region = [clawdata.lower[0]-0.1,
                                 clawdata.upper[0]+0.1,
                                 clawdata.lower[1]-0.1,
                                 clawdata.upper[1]+0.1]
    flagregions.append(flagregion)

    rundata.regiondata.regions = []
    # to specify regions of refinement append lines of the form
    #  [minlevel,maxlevel,t1,t2,x1,x2,y1,y2]

    flagregions = rundata.flagregiondata.flagregions  # initialized to []
    
    # dx = dy = 1deg, 4', 1', 30", 6", 2", 1", 1/3"":
    
    # Computational domain Variable Region - 1degree to 4min to 1min:
    # Level 3 below is 1 min
    # Note that this is a rectangle specified in the new way
    # (other regions below will force/allow more refinement)
    flagregion = FlagRegion(num_dim=2)
    flagregion.name = 'Region_domain_1hour_plus'
    flagregion.minlevel = 1
    flagregion.maxlevel = 2
    flagregion.t1 = 1*3600.
    flagregion.t2 = 1e9
    flagregion.spatial_region_type = 1  # Rectangle
    flagregion.spatial_region = [clawdata.lower[0]-0.1,
                                 clawdata.upper[0]+0.1,
                                 clawdata.lower[1]-0.1,
                                 clawdata.upper[1]+0.1]
    flagregions.append(flagregion)

    # Source Variable Region - 30sec to 30sec:
    flagregion = FlagRegion(num_dim=2)
    flagregion.name = 'Region_dtopo'
    flagregion.minlevel = 4
    flagregion.maxlevel = 4
    flagregion.t1 = 0.
    flagregion.t2 = 30.
    flagregion.spatial_region_type = 1  # Rectangle
    #source_region = [-185.0-0.1,-165.0+0.1,47.0-0.1,55.0+0.1]
    source_region = [-170.0-0.1,-158.0+0.1,51.0-0.1,56.0+0.1]
    flagregion.spatial_region = source_region
    flagregions.append(flagregion)

    ##So far, we can have a 1minute ocean for the first hour, and after
    ##that, we have guaranteed a 4 minute ocean only. For 30sec, there
    ##is a guaranteed 30sec region around the source

    #Now, what to do from time 0 to the first hour for 30sec computation follows.
    # Granting 30sec computation in the first hour.
    flagregion = FlagRegion(num_dim=2)
    flagregion.name = 'RegionWindow_time0_time1hr_1deg_30sec'
    flagregion.minlevel = 1
    flagregion.maxlevel = 4
    flagregion.t1 = 0.         
    flagregion.t2 = 1*3600.
    flagregion.spatial_region_type = 1  # Rectangle
    flagregion.spatial_region = [-170.0-0.1,-145.,18.0, 56.+0.1] ##includes source region
    #source_region = [-170.0-0.1,-158.0+0.1,51.0-0.1,56.0+0.1]
    flagregions.append(flagregion)

    #Now, what to do from time 1 hour to 2 hour for 30sec computation follows.
    flagregion = FlagRegion(num_dim=2)
    flagregion.name = 'RegionWindow_time1hr_time2hr_1deg_30sec'
    flagregion.minlevel = 1
    flagregion.maxlevel = 4
    flagregion.t1 = 1*3600.         
    flagregion.t2 = 2*3600.
    flagregion.spatial_region_type = 1  # Rectangle
    flagregion.spatial_region = [-170.0,-145.,18.0, 50.0] 
    flagregions.append(flagregion)

    #Now, what to do from time 2 hour to 3 hour for 30sec computation follows.
    flagregion = FlagRegion(num_dim=2)
    flagregion.name = 'RegionWindow_time2hr_time3hr_1deg_30sec'
    flagregion.minlevel = 1
    flagregion.maxlevel = 4
    flagregion.t1 = 2*3600.         
    flagregion.t2 = 3*3600.
    flagregion.spatial_region_type = 1  # Rectangle
    flagregion.spatial_region = [-165.0,-150.,18.0, 42.0] 
    flagregions.append(flagregion)

    #Now, what to do from time 3 hour to 4 hour for 30sec computation follows.
    flagregion = FlagRegion(num_dim=2)
    flagregion.name = 'RegionWindow_time3hr_time4hr_1deg_30sec'
    flagregion.minlevel = 1
    flagregion.maxlevel = 4
    flagregion.t1 = 3*3600.         
    flagregion.t2 = 4*3600.
    flagregion.spatial_region_type = 1  # Rectangle
    flagregion.spatial_region = [-162.0,-150.,18.0, 36.0] 
    flagregions.append(flagregion)

    #Now, what to do from time 4 hour to 4.5 hour for 30sec computation follows.
    flagregion = FlagRegion(num_dim=2)
    flagregion.name = 'RegionWindow_time4hr_time4hr30min_1deg_30sec'
    flagregion.minlevel = 1
    flagregion.maxlevel = 4
    flagregion.t1 = 4*3600.         
    flagregion.t2 = 4.5*3600.
    flagregion.spatial_region_type = 1  # Rectangle
    flagregion.spatial_region = [-162.0,-150.,18.0, 27.0] 
    flagregions.append(flagregion)

    #Now, what to do from time 4.5 hour onward for 30sec computation follows.
    flagregion = FlagRegion(num_dim=2)
    flagregion.name = 'RegionWindow_time4hr30min_onward_1deg_30sec'
    flagregion.minlevel = 1
    flagregion.maxlevel = 4
    flagregion.t1 = 4.5*3600.         
    flagregion.t2 = 1e9
    flagregion.spatial_region_type = 1  # Rectangle
    #flagregion.spatial_region = [-160.0,-152.,18.0, 22.0] 
    #Make this region above go over west to the Greater Island region
    #Make this region above up north to the Greater Island region
    flagregion.spatial_region = [-160.7,-152.,18.0, 22.6] 
    flagregions.append(flagregion)

    ## zoom-in'ers from Randy
    #regions.append([3, 3, 0., 2., -166,-162,52.5,54])
    #regions.append([1, 3, 0., 1*3600., -170,-145,19,55])
    #regions.append([1, 3, 1*3600., 2*3600., -170,-145,18,50])
    #regions.append([1, 3, 2*3600., 3*3600., -165,-150,18,42])
    #regions.append([1, 3, 3*3600., 4*3600., -162,-150,18,36])
    #regions.append([1, 3, 4*3600., 4.5*3600., -162,-150,18,27])
    #regions.append([1, 3, 4.5*3600., 1e9, -160,-152,18,22])

    if 1:
        # 36sec Topo Area - 1deg to 1min: 1 min ocean possible again 
        #                                 in slightly larger region after
        #                                 we release the 4 to 4.5 hr region
        flagregion = FlagRegion(num_dim=2)
        flagregion.name = 'RegionTopo36_1_comma_3_4hr30min_onward'
        flagregion.minlevel = 1
        flagregion.maxlevel = 3
        flagregion.t1 = 3600*4.5             #turn on at 4.5 hrs
        flagregion.t2 = 1e9
        flagregion.spatial_region_type = 1  # Rectangle
        #flagregion.spatial_region = [-164.994,-150.006,15.006,24.994]
        flagregion.spatial_region = [-162.0,-150.0,18.0,24.994]
        flagregions.append(flagregion)


    # Around Islands -  30sec:
    flagregion = FlagRegion(num_dim=2)
    flagregion.name = 'Region_Greater_Islands_30sec'
    flagregion.minlevel = 4
    flagregion.maxlevel = 4
    flagregion.t1 = 3600*4.0             #turn on at 4 hrs
    flagregion.t2 = 1e9
    flagregion.spatial_region_type = 1  # Rectangle
    flagregion.spatial_region = [-160.7,-154.54,18.5,22.6]
    flagregions.append(flagregion)

    # Closer Maui -  6sec:
    flagregion = FlagRegion(num_dim=2)
    flagregion.name = 'Region_Maui_6sec'
    flagregion.minlevel = 5
    flagregion.maxlevel = 5
    flagregion.t1 = tstart_finestgrid            #turn on at 4.25 hrs
    flagregion.t2 = 1e9
    flagregion.spatial_region_type = 1  # Rectangle
    flagregion.spatial_region = [-156.85, -155.8, 20.5, 21.19]
    flagregions.append(flagregion)

    # Closer Maui - 2sec
    flagregion = FlagRegion(num_dim=2)
    flagregion.name = 'Region_BigIsland_2sec'
    flagregion.minlevel = 6
    flagregion.maxlevel = 6
    flagregion.t1 = tstart_finestgrid            #turn on at 4.25 hrs
    flagregion.t2 = 1e9
    flagregion.spatial_region_type = 1  # Rectangle
    flagregion.spatial_region = [-155.3,-154.9,19.5,20.1]
    flagregions.append(flagregion)

    if 0:
        # Closer Maui - 1sec:
        flagregion = FlagRegion(num_dim=2)
        flagregion.name = 'Region_BigIsland_1sec'
        flagregion.minlevel = 7
        flagregion.maxlevel = 7
        flagregion.t1 = tstart_finestgrid            #turn on at 4.25 hrs
        flagregion.t2 = 1e9
        flagregion.spatial_region_type = 1  # Rectangle
        #flagregion.spatial_region = [-156.515, -156.4525, 20.888, 20.959]
        flagregion.spatial_region = [-155.11, -155.01, 19.7, 20.1]
        flagregions.append(flagregion)

    # Maui Site - require  1/3" grids:
    flagregion = FlagRegion(num_dim=2)
    flagregion.name = 'Region_Hilo_13sec'
    flagregion.minlevel = 8
    flagregion.maxlevel = 8
    flagregion.t1 = tstart_finestgrid
    flagregion.t2 = 1e9
    flagregion.spatial_region_type = 1  # Rectangle
    #flagregion.spatial_region = [-156.189, -156.17, 20.618, 20.628]
    #flagregion.spatial_region = [-156.5125, -156.494, 20.93, 20.9475]
    flagregion.spatial_region = [-155.11, -155.01, 19.7, 19.77]
    flagregions.append(flagregion)


    # Laupahoehoe
    fgmax_extent=[-155.248, -155.238, 19.987, 19.998]
    flagregion = FlagRegion(num_dim=2)
    flagregion.name = 'Region_Hilo_13sec'
    flagregion.minlevel = 8
    flagregion.maxlevel = 8
    flagregion.t1 = tstart_finestgrid
    flagregion.t2 = 1e9
    flagregion.spatial_region_type = 1  # Rectangle
    #flagregion.spatial_region = [-156.189, -156.17, 20.618, 20.628]
    #flagregion.spatial_region = [-156.5125, -156.494, 20.93, 20.9475]
    flagregion.spatial_region = [-155.252, -155.23, 19.98, 20.01]
    flagregions.append(flagregion)
    
    # ---------------
    # Gauges:
    # ---------------
    onethird = 1.0/(3.0*3600.)
    gauges = rundata.gaugedata.gauges = []
    # for gauges append lines of the form  [gaugeno, x, y, t1, t2]
    
    if 0:
        ###  GAUGES:  Site(1), beach-road(2),offshore-bay1(3), offshore-bay2(4), harborW(5), harborE(6)
        ###                8              9               10                11  (are south of 1,2,3,4 in Waihee preserve)
        ##                 7 at Waihee Point beach area
        ##                        12
        rundata.gaugedata.gauges.append([1,-156.5100, 20.9400, tstart_finestgrid + 120, 1.e10])
        gauge2_long = -156.51 + 16*onethird
        rundata.gaugedata.gauges.append([2,gauge2_long, 20.9400, tstart_finestgrid + 120, 1.e10])
        rundata.gaugedata.gauges.append([3,-156.5075,20.9400, tstart_finestgrid + 120, 1.e10])
        gauge4_long = -156.5075 + 11*onethird
        rundata.gaugedata.gauges.append([4,gauge4_long, 20.9400, tstart_finestgrid + 120, 1.e10])
        rundata.gaugedata.gauges.append([8,-156.5100, 20.9375, tstart_finestgrid + 120, 1.e10])
        gauge9_long = -156.51 + 16*onethird
        rundata.gaugedata.gauges.append([9,gauge9_long, 20.9375, tstart_finestgrid + 120, 1.e10])
        rundata.gaugedata.gauges.append([10,-156.5075,20.9375, tstart_finestgrid + 120, 1.e10])
        gauge11_long = -156.5075 + 11*onethird
        rundata.gaugedata.gauges.append([11,gauge11_long, 20.9375, tstart_finestgrid + 120, 1.e10])
        gauge12_long = -156.51 + 8*onethird; gauge12_lat = 20.9375 + 14*onethird;
        rundata.gaugedata.gauges.append([12,gauge12_long, gauge12_lat, tstart_finestgrid + 120, 1.e10])

        #Kahului Harbor
        gauge5_lat = 20.8975 + 21*onethird; gauge5_long = -156.48 -6*onethird;
        rundata.gaugedata.gauges.append([5,gauge5_long, gauge5_lat, tstart_finestgrid + 120, 1.e10])
        gauge6_lat = 20.8975 + 9*onethird; gauge6_long = -156.465 -10*onethird;
        rundata.gaugedata.gauges.append([6,gauge6_long, gauge6_lat, tstart_finestgrid + 120, 1.e10])

        #Waihee Point
        gauge7_lat = 20.95 + 8*onethird; gauge7_long = -156.5125;
        rundata.gaugedata.gauges.append([7,gauge7_long, gauge7_lat, tstart_finestgrid + 120, 1.e10])
    
    gaugefineon = tstart_finestgrid + 120
    gauges.append([1001, -162, 51.5, 0., 1.e10])
    gauges.append([1002, -159, 47., 0., 1.e10])
    gauges.append([1003, -157, 40., 3600., 1.e10])
    gauges.append([1004, -156, 30., 2.5*3600, 1.e10])
    gauges.append([1005, -155, 20.2, 4*3600, 1.e10])
    gauges.append([1006, -156.45, 20.95, 4*3600, 1.e10])
    gauges.append([1007, -155.08, 19.742, gaugefineon, 1.e10])    # Hilo entrance
    gauges.append([1008, -155.08, 19.730, gaugefineon, 1.e10])    # TS3?
    gauges.append([1010, -155.2398, 19.9936, gaugefineon, 1.e10]) # Laupahoehoe
    gauges.append([7760, -155.0553, 19.7308, gaugefineon, 1.e10]) # Hilo TG
        # https://tidesandcurrents.noaa.gov/stationhome.html?id=1617760
        # http://coastal.usc.edu/currents_workshop/problems/prob2.html

    # == setfixedgrids.data values ==
    #fixedgrids = rundata.fixed_grid_data.fixedgrids
    # THIS HAS BEEN DEPRECATED.  Use fgmax and/or fgout instead

    # -----------------------------
    # FGMAX GRIDS:
    # NEW STYLE STARTING IN v5.7.0
    # ------------------------------
    # set num_fgmax_val = 1 to save only max depth,
    #                     2 to also save max speed,
    #                     5 to also save max hs,hss,hmin
    rundata.fgmax_data.num_fgmax_val = 2

    fgmax_grids = rundata.fgmax_data.fgmax_grids  # empty list to start

    # Now append to this list objects of class fgmax_tools.FGmaxGrid
    # specifying any fgmax grids.

    #Set fgmax_extent: want the boundaries to be cell centers, so
    #can be an even integer plus some multiple of 1/3sec.  This will be true
    #if the decimal part is a multiple of .1, or .01, .005, or .0025 for
    #example based on how the computational domain was shifted.  This


    # Hilo
    fgmax_extent=[-155.1, -155.02, 19.71, 19.76]

    if 1:
        # Points on a uniform 2d grid:
        dx_fine = 1./(3600.)  # grid resolution at finest level
        fg = fgmax_tools.FGmaxGrid()
        fg.point_style = 2  # uniform rectangular x-y grid
        fg.x1 = fgmax_extent[0] #+ dx_fine/2.
        fg.x2 = fgmax_extent[1] #- dx_fine/2.
        fg.y1 = fgmax_extent[2] #+ dx_fine/2.
        fg.y2 = fgmax_extent[3] #- dx_fine/2.
        fg.dx = dx_fine
        fg.tstart_max =  tstart_finestgrid + 120  # when to start monitoring max values
        fg.tend_max = 1.e10                       # when to stop monitoring max values
        fg.dt_check = 30.            # target time (sec) increment between updating
                                    # max values
                                    # which levels to monitor max on
        fg.min_level_check = amrdata.amr_levels_max
        fg.arrival_tol = 1.e-2      # tolerance for flagging arrival
        fg.interp_method = 0        # 0 ==> pw const in cells, recommended
        fgmax_grids.append(fg)      # written to fgmax_grids.data
        
    # Laupahoehoe
    fgmax_extent=[-155.248, -155.238, 19.987, 19.998]

    if 1:
        # Points on a uniform 2d grid:
        dx_fine = 1./(3*3600.)  # grid resolution at finest level
        fg = fgmax_tools.FGmaxGrid()
        fg.point_style = 2  # uniform rectangular x-y grid
        fg.x1 = fgmax_extent[0] #+ dx_fine/2.
        fg.x2 = fgmax_extent[1] #- dx_fine/2.
        fg.y1 = fgmax_extent[2] #+ dx_fine/2.
        fg.y2 = fgmax_extent[3] #- dx_fine/2.
        fg.dx = dx_fine
        fg.tstart_max =  tstart_finestgrid + 120  # when to start monitoring max values
        fg.tend_max = 1.e10                       # when to stop monitoring max values
        fg.dt_check = 20.            # target time (sec) increment between updating
                                    # max values
                                    # which levels to monitor max on
        fg.min_level_check = amrdata.amr_levels_max
        fg.arrival_tol = 1.e-2      # tolerance for flagging arrival
        fg.interp_method = 0        # 0 ==> pw const in cells, recommended
        fgmax_grids.append(fg)      # written to fgmax_grids.data


    # == fgout_grids.data values ==
    # NEW IN v5.9.0
    # Set rundata.fgout_data.fgout_grids to be a list of
    # objects of class clawpack.geoclaw.fgout_tools.FGoutGrid:
    #fgout_grids = rundata.fgout_data.fgout_grids  # empty list initially

    if 0:
        # Grid over ocean with 1' resolution
        fgout_dx = 1./60   # target resolution
        fgout = fgout_tools.FGoutGrid()
        fgout.fgno = 1
        fgout.point_style = 2       # will specify a 2d grid of points
        fgout.output_format = 'binary32'
        fgout.x1 = -130.  # specify edges (fgout pts will be cell centers)
        fgout.x2 = -122.
        fgout.y1 = 38.5
        fgout.y2 = 50.5
        fgout.nx = int(round((fgout.x2 - fgout.x1) / fgout_dx)) # 480
        fgout.ny = int(round((fgout.y2 - fgout.y1) / fgout_dx)) # 720
        fgout.tstart = 0.
        fgout.tend = 60*60.
        fgout.nout = 121
        fgout_grids.append(fgout)    # written to fgout_grids.data

        # grid around Grays Harbor with 2" resolution
        fgout_dx = 1./1800   # target resolution
        fgout = fgout_tools.FGoutGrid()
        fgout.fgno = 2
        fgout.point_style = 2       # will specify a 2d grid of points
        fgout.output_format = 'binary32'
        fgout.x1 = -124.3  # specify edges (fgout pts will be cell centers)
        fgout.x2 = -123.75
        fgout.y1 = 46.8
        fgout.y2 = 47.1
        fgout.nx = int(round((fgout.x2 - fgout.x1) / fgout_dx)) # 990
        fgout.ny = int(round((fgout.y2 - fgout.y1) / fgout_dx)) # 540
        fgout.tstart = 0.
        fgout.tend = 60*60.
        fgout.nout = 121
        fgout_grids.append(fgout)    # written to fgout_grids.data

        # grid around Westport with 1/3" resolution
        fgout_dx = 1./(3*3600)   # target resolution
        fgout = fgout_tools.FGoutGrid()
        fgout.fgno = 3
        fgout.point_style = 2       # will specify a 2d grid of points
        fgout.output_format = 'binary32'
        fgout.x1 = -124.14  # specify edges (fgout pts will be cell centers)
        fgout.x2 = -124.08
        fgout.y1 = 46.85
        fgout.y2 = 46.92
        fgout.nx = int(round((fgout.x2 - fgout.x1) / fgout_dx)) # 648
        fgout.ny = int(round((fgout.y2 - fgout.y1) / fgout_dx)) # 756
        fgout.tstart = 0.
        fgout.tend = 60*60.
        fgout.nout = 121
        fgout_grids.append(fgout)    # written to fgout_grids.data



    #  ----- For developers ----- 
    # Toggle debugging print statements:
    amrdata.dprint = False      # print domain flags
    amrdata.eprint = False      # print err est flags
    amrdata.edebug = False      # even more err est flags
    amrdata.gprint = False      # grid bisection/clustering
    amrdata.nprint = False      # proper nesting output
    amrdata.pprint = False      # proj. of tagged points
    amrdata.rprint = False      # print regridding summary
    amrdata.sprint = False      # space/memory output
    amrdata.tprint = False      # time step reporting each level
    amrdata.uprint = False      # update/upbnd reporting
    
    return rundata

if __name__ == '__main__':
    # Set up run-time parameters and write all data files.
    import sys
    from clawpack.geoclaw import kmltools
    rundata = setrun(*sys.argv[1:])
    rundata.write()
    
    kmltools.make_input_data_kmls(rundata)
