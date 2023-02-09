"""
 Title:         The Voce Slip Hardening Asaro Inelasticity Model
 Description:   Predicts primary creep via crystal plasticity
 Author:        Janzen Choi
"""

# Libraries
import matplotlib.pyplot as plt
from neml import elasticity, drivers
from neml.cp import crystallography, slipharden, sliprules, inelasticity, kinematics, singlecrystal, polycrystal
from neml.math import rotations

# Fixed Parameters
YOUNGS      = 211000.0
POISSONS    = 0.3
S_RATE      = 1.0e-4
E_RATE      = 1.0e-4
E_MAX       = 0.005
HOLD        = 11500.0 * 3600.0
NUM_STEPS   = 100
MAX_ITER    = 16
MAX_DIVIDE  = 4
MIN_DATA    = 50
VERBOSE     = False

# Material parameters
vsh_ts = 83.68041279
vsh_b  = 3.73928443
vsh_t0 = 3.05569439
ai_g0  = 0.26831762
ai_n   = 14.04134645

# Model parameters
orientation_file = "input_orientations.csv"
lattice_a        = 1.0
slip_direction   = [1,1,0]
slip_plane       = [1,1,1]
num_threads      = 8

# Extract grain orientations
file = open(orientation_file, "r")
grain_orientations = []
for line in file.readlines():
    data = line.replace("\n","").split(",")
    phi_1 = float(data[0])
    Phi   = float(data[1])
    phi_2 = float(data[2])
    grain_orientations.append(rotations.CrystalOrientation(phi_1, Phi, phi_2, angle_type="degrees", convention="bunge"))
file.close()

# Define lattice structure
elastic_model = elasticity.IsotropicLinearElasticModel(YOUNGS, "youngs", POISSONS, "poissons")
lattice = crystallography.CubicLattice(lattice_a)
lattice.add_slip_system(slip_direction, slip_plane)

# Define and run model
strength_model  = slipharden.VoceSlipHardening(vsh_ts, vsh_b, vsh_t0)
slip_model      = sliprules.PowerLawSlipRule(strength_model, ai_g0, ai_n)
ai_model        = inelasticity.AsaroInelasticity(slip_model)
ep_model        = kinematics.StandardKinematicModel(elastic_model, ai_model)
cp_model        = singlecrystal.SingleCrystalModel(ep_model, lattice, verbose=False, miter=1, max_divide=MAX_DIVIDE)
vshai_model     = polycrystal.TaylorModel(cp_model, grain_orientations, nthreads=num_threads)
tensile_results = drivers.uniaxial_test(vshai_model, E_RATE, T=300, verbose=VERBOSE, emax=E_MAX, nsteps=NUM_STEPS)
strain_list = list(tensile_results['strain'])
stress_list = list(tensile_results['stress'])

# Plot curve
plt.scatter(strain_list, stress_list, color="b")
plt.savefig("creep.png")