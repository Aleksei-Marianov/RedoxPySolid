**Modelling of electrochemical responses.**

Package allows for explicit modelling of the heterogeneous electrochemical systems.
The full description of the method is given in the paper <https://pubs.acs.org/doi/abs/10.1021/acs.analchem.1c01286>

**Installation:**
```
pip install -i https://test.pypi.org/simple/ RedoxPySolid
```

**Example:**

```python
# The package is compiled to work with Windows OS
# each simulation run takes several minutes to complete

from RedoxPySolid.activeLayer import ElectrochemicallyActiveLayer
from RedoxPySolid.CV import CV
from RedoxPySolid.VFSWV import VFSWV
import matplotlib.pyplot as plt

# describe the characteristics of the surface layer
layer_params = [{'dist_type': 'lorentz',
        'g0': 0.35*10**(-9),
        'e0': -0.2,
        'sigma_e0': 0.04,
        'log_k0': 1.2,
        'sigma_log_k0': 0.1,
        'a': 0.5,
        'z': 1},
        {'dist_type': 'lorentz',
        'g0': 0.2*10**(-9),
        'e0': 0,
        'sigma_e0': 0.04,
        'log_k0': 0.5,
        'sigma_log_k0': 0.1,
        'a': 0.5,
        'z': 2}]

# create a class instance of the surface layer and visualise the output as 2D map
layer = ElectrochemicallyActiveLayer(31, (-0.4, 0.2), 31, (0, 2), layer_params, loading_cutoff=10**(-13))
layer.visualize_surface_kinetics()
output = layer.compressed_data
print(output)

# define the cyclic voltammetry (CV) parameters
cv_params = {'e_start': 0.3,
        'e_end': -0.4,
        'scan_rate': 0.1,
        'resistance': 10,
        'capacitance': 100*10**(-6)}

# simulate the CV and visualise the output
cv_scan = CV(layer, cv_params)
y = cv_scan.cv_full_response
x = cv_scan.cv_pulse_sequence
plt.plot(x, y)
plt.ylabel('j, mA/cm$^2$')
plt.xlabel('E, V')
plt.show()

# define the parameters of the variable frequency square wave voltammetry simulation
vf_swv_params = {'e_start': 0.1,
        'e_step': -0.01,
        'e_end': -0.5,
        'amplitude': 0.025,
        'log_frequency_min': 0,
        'log_frequency_max': 3,
        'resistance': 10,
        'capacitance': 100*10**(-6)}

# simulate the VF-SWV and visualise the output
vf_swv_scan = VFSWV(layer, vf_swv_params)
vf_swv_scan.visualize_colormap_3D()
vf_swv_scan.visualize_colormap_2D()
```
