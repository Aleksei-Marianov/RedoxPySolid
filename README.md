**Modelling of electrochemical responses.**

Package allows for explicit modelling of the heterogeneous electrochemical systems.
The full description of the method is given in the 'paper <https://pubs.acs.org/doi/abs/10.1021/acs.analchem.1c01286>'_

**Example:**
::
  from RedoxPySolid.activeLayer import ElectrochemicallyActiveLayer
  from RedoxPySolid.VFSWV import VFSWV
  import numpy as np

  scan_params = {'e_start': -0.5,
                  'e_step': -0.01,
                  'e_end': -1.1,
                  'amplitude': 0.025,
                  'log_frequency_min': 0,
                  'log_frequency_max': 3,
                  'resistance': 12.8,
                  'capacitance': 92*10**(-6)}

  electrode_params = [{'dist_type': 'lorentz',
            'g0': 0.065*10**(-9)+3*0.006*10**(-9),
            'e0': -0.949,
            'sigma_e0': 0.15,
            'log_k0': 2.146,
            'sigma_log_k0': 0.03,
            'a': 0.5,
            'z': 1},
            {'dist_type': 'lorentz',
            'g0': 0.10*10**(-9),
            'e0': -0.949,
            'sigma_e0': 0.08,
            'log_k0': 2.114,
            'sigma_log_k0': 0.04,
            'a': 0.5,
            'z': 1},
              {'dist_type': 'lorentz',
            'g0': 0.05*10**(-9),
            'e0': -0.949,
            'sigma_e0': 0.07,
            'log_k0': 2.079,
            'sigma_log_k0': 0.04,
              'a': 0.5,
              'z': 1},
            {'dist_type': 'lorentz',
            'g0': 0.01*10**(-9),
            'e0': -0.949,
            'sigma_e0': 0.07,
            'log_k0': 1.978,
            'sigma_log_k0': 0.1,
            'a': 0.5,
            'z': 1},
            {'dist_type': 'lorentz',
            'g0': 0.008*10**(-9),
            'e0': -0.949,
            'sigma_e0': 0.07,
            'log_k0': 1.845,
            'sigma_log_k0': 0.1,
            'a': 0.5,
            'z': 1},
            {'dist_type': 'lorentz',
            'g0': 0.10*10**(-9),
            'e0': -0.949,
            'sigma_e0': 0.12,
            'log_k0': 1.70,
            'sigma_log_k0': 0.5,
            'a': 0.5,
            'z': 1},
              {'dist_type': 'lorentz',
            'g0': 0.10*10**(-9),
            'e0': -0.935,
            'sigma_e0': 0.12,
            'log_k0': 0,
            'sigma_log_k0': 0.7,
              'a': 0.5,
              'z': 1},
              {'dist_type': 'lorentz',
            'g0': 0.075*10**(-9),
            'e0': -0.830,
            'sigma_e0': 0.12,
            'log_k0': 0,
            'sigma_log_k0': 0.7,
              'a': 0.5,
              'z': 1},
              {'dist_type': 'lorentz',
            'g0': 0.005*10**(-9),
            'e0': -0.78,
            'sigma_e0': 0.12,
            'log_k0': 0,
            'sigma_log_k0': 0.7,
              'a': 0.5,
              'z': 1},
              {'dist_type': 'lorentz',
            'g0': 0.05*10**(-9),
            'e0': -0.64,
            'sigma_e0': 0.12,
            'log_k0': 0,
            'sigma_log_k0': 0.7,
              'a': 0.5,
              'z': 1}]

  electrode = ElectrochemicallyActiveLayer(41, (-1.5, -0.4), 41, (-0.5, 2.5), electrode_params, loading_cutoff=10**(-14))
  electrode.visualize_surface_kinetics()

  cotpp_noncov_cc = VFSWV(surface_layer=electrode, vf_swv_input_params = scan_params)
  cotpp_noncov_cc.visualize_colormap_2D()
  cotpp_noncov_cc.visualize_colormap_3D()

