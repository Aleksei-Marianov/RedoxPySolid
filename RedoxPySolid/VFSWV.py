# --------------------------------------------------------------------------
                    # Written by Aleksei Marianov
# --------------------------------------------------------------------------  

"""
Compute a 2D VF-SWV voltammogram. The parameters of the 
redox active layer are passed as an instance of the ElectrochemicallyActiveLayer.
If ElectrochemicallyActiveLayer is not given (explicit None), then the 
non-faradic response is computed. The non-faradic colormap could be used to find 
resistance and capacitance of the system.

The class VFSWV inherits from the class SWV.
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import numpy as np

from RedoxPySolid.activeLayer import ElectrochemicallyActiveLayer
from RedoxPySolid.SWV import SWV


class VFSWV(SWV):
    """
    Class describes the electrochemical response to the VF-SWV
    pulse sequence. This is a 2D method whihc is thoroughly described here:
    https://pubs.acs.org/doi/abs/10.1021/acs.analchem.1c01286

    Note: all units are strictly metric (V, F, Ohm, s)!

    Class attributes
    ----------
    None

    Class instance attributes
    ----------
    np.ndarrays containing non-faradic responses:
    self.vf_swv_data: np.ndarray, 2D array of VF-SWV response (z coordinate). The default values are in Amp 
                    and the sign follows the IUPAC convention;
    self.vf_swv_potential_domain: np.ndarray, 2D array for the y coordinate on the VF-SWV plot;
    self.vf_swv_frequency_domain: np.ndarray, 2D array for the x coordinate on the VF-SWV plot;

    Methods
    -------
    __init__(self) -> None. Constructor method bulding the SWV instance attributes.
    visualize_colormap_2D(self,
                        fig_size = (6, 5),
                        color_pallet = 'jet',
                        cbar_accuracy = "%.0f") -> None. Show visual representation of the VF-SWV colormap;
    visualize_colormap_3D(self,
                        fig_size = (6, 5),
                        color_pallet = 'jet') -> None. Show 3D map of the VF-SWV response.
    """
    def __init__(self, surface_layer: ElectrochemicallyActiveLayer, 
                vf_swv_input_params: dict,
                pulse_resolution=100,
                frequency_domain_resolution = 61) -> None:
        
        """
        VF-SWV class constructor method.

        Parameters:
        -----------
        surface_layer: ElectrochemicallyActiveLayer.
            Important: value None could be passed and then only non-faradic responses will be returned;

        self, surface_layer: ElectrochemicallyActiveLayer or None. The class instance of the electrochemically active layer.
            If only non-faradic response is reuired, None should be passed;
        vf_swv_input_params: dict, full description of the VF-SWV experiment,
            Example:
                {'e_start': 0.4,
                'e_step': -0.002,
                'e_end': -0.4,
                'amplitude': 0.005,
                'log_frequency_min': 0,
                'log_frequency_max': 3,
                'resistance': 10,
                'capacitance': 100*10**(-6)};
        pulse_resolution: int, resolution of each SWV pulse, default value 100;
        frequency_domain_resolution: int, resolution across the frquency domain, default value 61;
        
        Returns:
        --------
        None, but creates the instance attributes (vide supra);
        """

        # generate points across the frequency domain
        log_freq_min = vf_swv_input_params['log_frequency_min']
        log_freq_max = vf_swv_input_params['log_frequency_max']

        # define placeholders for the output 2D arrays
        self.vf_swv_data = []
        self.potential_scale = []

        # generate a range of dicts with the input data for single-frequency SWVs
        log_f_range = np.linspace(log_freq_max, log_freq_min, frequency_domain_resolution)
        freqs = 10**(log_f_range)
        for i, (log_f, frequency) in enumerate(zip(log_f_range, freqs)):
            
            # bug fix: create a local copy of the input dictionary to make sure the external 
            # variable is available for the further use.
            
            swv_params = vf_swv_input_params
            swv_params["log_freq"] = log_f
            super().__init__(surface_layer, vf_swv_input_params, pulse_resolution)
            self.vf_swv_data.append(self.swv_data/frequency)
            if i == 0:
                self.potential_scale = self.swv_pontential_scale

        self.vf_swv_data = np.array(self.vf_swv_data)
        self.vf_swv_potential_domain, self.vf_swv_frequency_domain = np.meshgrid(self.potential_scale, log_f_range)
        
    def visualize_colormap_2D(self,
                            fig_size = (6, 5),
                            color_pallet = 'jet',
                            cbar_accuracy = "%.0f") -> None:
        """
        Builds a 2D map of the VF-SWV voltammogram.
        Important: for the sake of convenience the currents are always displayed as positive values
        and the units are converted to microampers.

        Parameters:
        -----------
        self, class instance;
        fig_size = (6, 5), fugure size. Default value is used;
        color_pallet = 'jet'; coloramp for the plotting;
        cbar_accuracy = "%.0f", the number of significant digits on the colorbar;

        Returns:
        --------
        None, builds a fugure.
        """
        font = {'family': 'serif', 'serif': 'Calibri', 'weight': 'bold', 'size': 11}
        plt.rc('font', **font)
        f, ax = plt.subplots(1, 1, figsize=fig_size)

        # always display differential current as positive number
        if self.potential_scale[0] > self.potential_scale[-1]:
            cont = ax.contourf(self.vf_swv_frequency_domain, 
                                self.vf_swv_potential_domain, 
                                -10**(6)*self.vf_swv_data, 200, 
                                cmap=color_pallet)
            cbar = f.colorbar(cont, ax=ax, format=cbar_accuracy)
            cbar.set_label('-\u2206 $j$/$f$, \u00B5C/cm\u00B2', weight='bold')

        else:
            cont = ax.contourf(self.vf_swv_frequency_domain, 
                                self.vf_swv_potential_domain, 
                                10**(6)*self.vf_swv_data, 200, 
                                cmap=color_pallet)
            cbar = f.colorbar(cont, ax=ax, format=cbar_accuracy)
            cbar.set_label('\u2206 $j$/$f$, \u00B5C/cm\u00B2', weight='bold')

        ax.set_xlabel('log[$f$(Hz)]', weight='bold')
        ax.set_ylabel('E, V', weight='bold')
        plt.tight_layout()
        plt.show()
    
    def visualize_colormap_3D(self,
                            fig_size = (6, 5),
                            color_pallet = 'jet') -> None:
        """
        Builds a 3D map of the VF-SWV voltammogram.
        Important: for the sake of convenience the currents are always displayed as positive values
        and the units are converted to microampers.

        Parameters:
        -----------
        self, class instance;
        fig_size = (6, 5), fugure size. Default value is used;
        color_pallet = 'jet'; coloramp for the plotting;

        Returns:
        --------
        None, builds a fugure.
        """

        font = {'family': 'serif', 'serif': 'Calibri', 'weight': 'bold', 'size': 11}
        plt.rc('font', **font)
        
        f= plt.figure(figsize=fig_size)
        ax = f.gca(projection="3d")

        # always display differential current as positive number
        if self.potential_scale[0] > self.potential_scale[-1]:
            cont = ax.plot_surface(self.vf_swv_frequency_domain, 
                                self.vf_swv_potential_domain, 
                                -10**(6)*self.vf_swv_data, cmap=color_pallet)
        else:
            cont = ax.plot_surface(self.vf_swv_frequency_domain, 
                                self.vf_swv_potential_domain, 
                                10**(6)*self.vf_swv_data, cmap=color_pallet)

        ax.set_xlabel('log[$f$(Hz)]', weight='bold')
        ax.set_ylabel('E, V', weight='bold')
        ax.set_zlabel('\u2206 $j$/$f$, \u00B5C/(cm\u00B2)', weight='bold')
        plt.tight_layout()
        plt.show()


# testing and example:
if __name__ == "__main__":
    electrode_params = [{'dist_type': 'normal',
                        'g0': 0.5*10**(-9),
                         'e0': 0,
                         'sigma_e0': 0.01,
                         'log_k0': 2.5,
                         'sigma_log_k0': 0.01,
                         'a': 0.5,
                         'z': 1}]

    vf_swv_params = {'e_start': 0.4,
                'e_step': -0.002,
                'e_end': -0.4,
                'amplitude': 0.005,
                'log_frequency_min': 0,
                'log_frequency_max': 3,
                'resistance': 10,
                'capacitance': 100*10**(-6)}

    layer = ElectrochemicallyActiveLayer(11, (-0.4, 0.4), 11, (2, 3), electrode_params, loading_cutoff=10**(-12))
    layer.visualize_surface_kinetics()
    scan = VFSWV(layer, vf_swv_params)
    scan.visualize_colormap_3D()
