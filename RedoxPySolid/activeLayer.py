# --------------------------------------------------------------------------
                    # Written by Aleksei Marianov
# --------------------------------------------------------------------------  

"""                
Generate a mathematical description of the electrochemically active layer.

The surface layer is modeled as a combination of multiple redox couples.
It is assumed that the Butler-Volmer model of electrochemical kinetics
is applicable and correct.
All added components are characterised as statistical distributions.

The parameters are:
Redox potential E0, V
Standard reaction constant k0, s^(-1)
Electron transfer symmetry coefficient a,
Number of electrons z,
Surface loading g0: mol/cm2

In-depth description of the physical model is available here:
https://pubs.acs.org/doi/abs/10.1021/acs.analchem.1c01286
"""

from ctypes import c_double
import numpy as np
from scipy.stats import norm, cauchy

import matplotlib.pyplot as plt
import matplotlib.pylab as pl
from matplotlib.ticker import FormatStrFormatter


def _append_a_component(dist_type: str, 
                        g0: float, 
                        e0: float, 
                        sigma_e0: float, 
                        e_axis_resolution: int,
                        e_range: np.ndarray, 
                        log_k0: float, 
                        k0_log_range: np.ndarray,
                        sigma_log_k0: float, 
                        k0_resolution: int, 
                        a: float, 
                        z: int,
                        _resolution_boost_modifier = 1001) -> tuple:
    """
    Adds a redox active component to the surface. This is supposed to be a private method.
    The type of distribution across E axis is defined by the user.
    Distribution across log(k0) axis is always normal.

    Parameters:
    -----------
    dist_type: str, type of distribution across E axis. Allowed values: 'normal', 'lorentz'
    g0: float, surface loading of the target component;
    e0: float, most likely equilibrium potential of the target component;
    sigma_e0: float, width of the statistical distribution across the potential axis;
    e_axis_resolution: int, resolution of the statistical analysis across the E axis 
            (15-20 is considered to be low resolution and 40-50 is considered a high-definition simulaiton);                
    e_range: np.ndarray, the window over which the statistical distribution will be applied;
    k0_log: float, Log10 of the reaction rate constant;
    k0_log_range: np.ndarray, define a window over which the reaction rates will be computed;
    sigma_log_k0: float, the width of the statistical distribution across the rate axis;
    k_resolution: int, resolution across the rate axis;
    a: float, symmetry coefficient for this particular component;
    z: int, number of electrons transferred in the reaction;
    _resolution_boost_modifier: default 1001, designed to assure correct integral for the statistical curve;
    Returns:
    --------
    tuple (2D arrays of: loadings, a coefficients and z values)
    """
    assert dist_type == 'normal' or dist_type == 'lorentz', 'Unknown distribution requested.'
    loadings_array = []

    # a major bug fix: if the width of the statistical distribution is close to the digital resolution of the axis,
    # the integrl for norm and cauchy drops well below 1 as a result of non-continuity of the scipy funcitons.
    # The temporary variable is introduced which adopts the original e_range as a mean across rows in 2D matrix.
    # The enhancement transformaiton is applied across both E and log(k0) axes.

    e_wider = np.linspace((3*e_range[0] - e_range[1])/2, (3*e_range[-1] - e_range[-2])/2, e_axis_resolution*_resolution_boost_modifier)
    e_2d = np.reshape(e_wider, (-1, _resolution_boost_modifier))

    if dist_type == 'normal':
        dist  = norm.pdf(e_wider, loc=e0, scale=sigma_e0)
        dist_2d = np.reshape(dist, (-1, _resolution_boost_modifier))
        g_second_across_e = g0*np.array([np.trapz(i, j) for i, j in zip(dist_2d, e_2d)])
        
    else:
        dist  = cauchy.pdf(e_wider, loc=e0, scale=sigma_e0)
        dist_2d = np.reshape(dist, (-1, _resolution_boost_modifier))
        g_second_across_e = g0*np.array([np.trapz(i, j) for i, j in zip(dist_2d, e_2d)])

    log_k_wider = np.linspace((3*k0_log_range[0] - k0_log_range[1])/2, (3*k0_log_range[-1] - k0_log_range[-2])/2, 
                                k0_resolution*_resolution_boost_modifier)
    log_k_2d_wide = np.reshape(log_k_wider, (-1, _resolution_boost_modifier))
    dist = norm.pdf(log_k_wider, loc=log_k0, scale=sigma_log_k0)
    dist_2d = np.reshape(dist, (-1, _resolution_boost_modifier))
    p_f_second = np.array([np.trapz(i, j) for i, j in zip(dist_2d, log_k_2d_wide)])

    for g in g_second_across_e:
        g_dist_across_k = g * p_f_second
        loadings_array.append(g_dist_across_k)

    loadings_array = np.array(loadings_array)
    a_array = a * np.ones(loadings_array.shape)
    z_array = z * np.ones(loadings_array.shape)

    return loadings_array, a_array, z_array


def _build_surface_layer(e_axis_resolution: int, 
                        e_dist_bounds: tuple, 
                        log_k_axis_resolution: int,
                        log_k0_dist_bounds: tuple, 
                        params_list: list) -> dict:
    """
    Builds an input matrix which describes the behaviour of the surface layer.
    This is supposed to be a private method.
    The return values form the base of the ElectrochemicallyActiveLayer class. The methods provide for visualisation, 
    data saving, etc.
    
    Parameters:
    -----------
    e_axis_resolution: int, resolution across the axis of potentials;
    e_dist_bounds: tuple, 2 values describing the potential window to apply;
    log_k_axis_resolution: int, resolution across the k0 axis;
    log_k0_dist_bounds: tuple, 2 values describing the window of the reaction rates;
    params_list: list of dictionaries where each dictionary contains complete description of the 
    a particular component to append. These are parsed and passed to the "append_component..." functions;
    loading_cut_off, float, default value 10**(-13). This cuts off any minor components which will 
    have negligible contribution into the overall redox reaction on the surface.

    Returns:
    --------
        dict of 2D arrays of equilibrium potentials, kinetics constants, surface loadings of subcomponents, a and z coefficients)
    """
    assert e_dist_bounds[0] < e_dist_bounds[1], "The E boundaries are defined in incorrect order."
    assert log_k0_dist_bounds[0] < log_k0_dist_bounds[1], "The log(k0) boundaries are defined in incorrect order."

    e_range = np.linspace(min(e_dist_bounds), max(e_dist_bounds), e_axis_resolution)
    k_log_range = np.linspace(min(log_k0_dist_bounds), max(log_k0_dist_bounds), log_k_axis_resolution)

    loading_arr = []
    a_arr = []
    z_arr = []

    # The parameters of each component are stacked together here.
    # If the a and z parameters of a new component coincide with the one which is already added,
    # then these two matrices are added. Otherwise - a new matrix is created.

    for i, dictionary in enumerate(params_list):
        dictionary['e_axis_resolution'] = e_axis_resolution
        dictionary['e_range'] = e_range
        dictionary['k0_log_range'] = k_log_range
        dictionary['k0_resolution'] = log_k_axis_resolution
        gs, a_s, z_s = _append_a_component(**dictionary)

        if i == 0:
            a_arr.append(a_s)
            loading_arr.append(gs)
            z_arr.append(z_s)
        else:
            if np.mean(a_arr[-1]) == np.mean(a_s[-1][-1]) and np.mean(z_arr[-1]) == np.mean(z_s[-1]):
                loading_arr[- 1] = np.add(loading_arr[- 1], gs)
            else:
                a_arr.append(a_s)
                loading_arr.append(gs)
                z_arr.append(z_s)

    # The list of 2D arrays is collated for further use.
    k_2d, e_2d = [], []

    for i in range(len(loading_arr)):
        yy, xx = np.meshgrid(k_log_range, e_range)
        k_2d.append(yy)
        e_2d.append(xx)
    return {'arrays_of_potentials': e_2d, 
            'arrays_of_kinetic_constants': k_2d,
            'arrays_of_loadings': loading_arr, 
            'arrays_of_symmetry_coef': a_arr,
            'arrays_of_z': z_arr}


class ElectrochemicallyActiveLayer:
    """
    Class represents the behaviour of the electrochemically active surface layer.

    Class attributes
    ----------
    None
    Class instance attributes
    ----------
    self.surface_layer: dictionary of the lists contaninng the surface distributions
        where g0 = f(E, a, z);
    self.loading_cutoff: loading cutoff limit;
    self.e_axis_resolution: resolution of statistical analysis. The higher the resolution,
        the lower the computational speed;
    self.log_k_axis_resolution: resolution of statistical analysis. The higher the resolution,
        the lower the computational speed;
    self.loading_cutoff: the components below cutoff threshold are removed as they provide almost not
        contribution to the current while wasting a lot of time for computaiton;
    self.compressed_data: surafce layer parameters prepared for DLL module.

    Methods
    -------
    __init__(self, e_axis_resolution: int,
                 e_dist_bounds: tuple,
                 log_k_axis_resolution: int,
                 log_k0_dist_bounds: tuple,
                 params_list: list,
                 export_folder: str,
                 loading_cutoff=10**(-13)) -> None
                 Class instance constructor method.
    visualize_surface_kinetics(self) -> None
        Gives a visual representation of the kinetic distribution.
    _prepare_data_for_computation(self) -> dict
        Linearises 2D arrays before they could be fed to C++ funcitons.
    """
    def __init__(self, e_axis_resolution: int,
                 e_dist_bounds: tuple,
                 log_k_axis_resolution: int,
                 log_k0_dist_bounds: tuple,
                 params_list: list,
                 loading_cutoff=10**(-13)):

        """
        Provides the constructor method for the electrochemically active surface layer.

        Parameters:
        ----------
        e_axis_resolution : int
            An int representing the resolution across E axis "observed" by a researcher.
        e_dist_bounds : tuple(lower cutoff E, higher cutoff E)
            Describes the region of interest where the redox active material is expected to give
            some electrochemical response.
        log_k_axis_resolution : int
            An int representing the resolution across log(k0) axis.
        log_k0_dist_bounds: tuple (lower cutoff log(k0), higher cutoff log(k0)
            Provides bounds of base for the log(k0) values to be projected.
        params_list: list
            The most important part containing a list of dictionaries. Each dictionary contains the full description
            of each active component. For example, the list below describes a layer with 2 redox couples. Both
            display Lorentz distribution in the E0 domain. First is a 1-electron transfer process and second
            is a 2-electron reaction.

                params = [{'dist_type': 'lorentz',
                'g0': 0.035*10**(-9),
                'e0': -0.2,
                'sigma_e0': 0.04,
                'log_k0': 1.2,
                'sigma_log_k0': 0.1,
                'a': 0.5,
                'z': 1},
                {'dist_type': 'lorentz',
                'g0': 0.02*10**(-9),
                'e0': -0.2,
                'sigma_e0': 0.04,
                'log_k0': 0.5,
                'sigma_log_k0': 0.1,
                'a': 0.5,
                'z': 2}]
        loading_cutoff: float.
            Defines the lowest loading which could be "seen". It is assumed that if the loading is too low,
            it will not give a significant signal and this could be ignored to save time. Default value 10 ** (-13) mol/cm2

        Returns:
        --------
        None, but creates the instance attributes (vide supra);
        """

        self.surface_layer = _build_surface_layer(e_axis_resolution=e_axis_resolution,
                                                  e_dist_bounds=e_dist_bounds,
                                                  log_k_axis_resolution=log_k_axis_resolution,
                                                  log_k0_dist_bounds=log_k0_dist_bounds,
                                                  params_list=params_list)
        self.loading_cutoff = loading_cutoff
        self.e_axis_resolution = e_axis_resolution
        self.log_k_axis_resolution = log_k_axis_resolution
        self.loading_cutoff = loading_cutoff
        self.compressed_data = self._prepare_data_for_computation()

    def visualize_surface_kinetics(self) -> None:
        """
        The method provides a visualisation of the surface redox kinetics.
        3D figure is drawn by default.

        Returns:
        --------
        None.
        """

        font = {'family': 'serif', 'serif': 'Arial', 'weight': 'bold', 'size': 11}
        plt.rc('font', **font)
        fig = plt.figure(figsize=(8, 6))
        e_s, k_s, g_s, a_s, z_s = list(self.surface_layer.values())
        colors = pl.cm.terrain(np.linspace(0, 1, len(e_s)))
        ax1 = fig.add_subplot(projection='3d', azim=30, elev=25)

        for i, (e, k, g, a, z, color) in enumerate(zip(e_s, k_s, g_s, a_s, z_s, colors)):

            potentials = e.flatten()
            constants = k.flatten()
            loadings = g.flatten()

            # Labeling of the plots is to be implemented
            # label = f'Process with a={a[0]} and z={z[0]}'

            width = (np.max(e) - np.min(e)) / (self.e_axis_resolution * 2)
            depth = (np.max(k) - np.min(k)) / (self.log_k_axis_resolution * 2)
            for j, loading in enumerate(loadings):
                if loading < self.loading_cutoff:
                    potentials[j] = np.nan
                    constants[j] = np.nan
                    loadings[j] = np.nan
            potentials, constants, loadings = potentials[~np.isnan(potentials)], constants[~np.isnan(constants)], \
                                                loadings[~np.isnan(loadings)]
            bottom = np.zeros_like(loadings)
            ax1.bar3d(potentials, constants, bottom, width, depth, loadings*10**(12),
                      color=color, shade=True, edgecolor='black', linewidth=0.05, alpha=0.8)

        ax1.grid(False)
        ax1.set_xlabel('E, V vs NHE', weight='bold')
        ax1.set_ylabel('log[k, s$^{-1}$]', weight='bold')
        ax1.set_zlabel('$\u0393$$_{EA}$, pmol/cm$^{-2}$', weight='bold')
        ax1.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        ax1.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        ax1.zaxis.set_major_formatter(FormatStrFormatter('%.0f'))
        plt.subplots_adjust(0, 0, 1, 1)
        plt.show()

    def _prepare_data_for_computation(self) -> dict:
        """
        Prepares data for the fast computational assessment.
        Returns:
        --------
        dict {'E0': potentials, 
            'k0': kinetic_constants, 
            'g': loadings, 
            'a': alphas, 
            'z': z_values}
        """
        
        # combine and linearize the 2D arrays for C++ module to work.

        e_full = np.concatenate(self.surface_layer['arrays_of_potentials'])
        g_full = np.concatenate(self.surface_layer['arrays_of_loadings'])
        k_full = 10**np.concatenate(self.surface_layer['arrays_of_kinetic_constants'])
        a_full = np.concatenate(self.surface_layer['arrays_of_symmetry_coef'])
        z_full = np.concatenate(self.surface_layer['arrays_of_z'])
        potentials, kinetic_constants = e_full.flatten(), k_full.flatten()
        loadings, alphas, z_values = g_full.flatten(), a_full.flatten(), z_full.flatten()
        
        original_size = len(loadings)
        # here the time optimization is performed. The values below a pre-determined limit are discarded.
        # The weeding of small values is done by replacing them with NaNs.

        for i, g_s in enumerate(loadings):
            if g_s < self.loading_cutoff:
                potentials[i] = np.nan
                kinetic_constants[i] = np.nan
                loadings[i] = np.nan
                alphas[i] = np.nan
                z_values[i] = np.nan
        potentials, kinetic_constants, = potentials[~np.isnan(potentials)], \
                                            kinetic_constants[~np.isnan(kinetic_constants)]
        loadings, alphas = loadings[~np.isnan(loadings)], alphas[~np.isnan(alphas)]
        z_values = z_values[~np.isnan(z_values)]

        # cast values to c_double for the C++ module
        potentials = potentials.astype(c_double)
        kinetic_constants = kinetic_constants.astype(c_double)
        loadings = loadings.astype(c_double)
        alphas = alphas.astype(c_double)
        z_values = z_values.astype(c_double)

        # inform the user of the performance optimisation:

        print(f'Reduction of matrix size {int(100 - 100 * round(len(loadings) / original_size, 2))}%')
        print(f'The loss of loading to size reduction {round(100 - 100 * np.sum(loadings) / np.sum(g_full), 3)}%')
        print(f'Surface loading passed to computation is {np.sum(loadings)}')
        return {'E0': potentials, 
                'k0': kinetic_constants, 
                'g': loadings, 
                'a': alphas, 
                'z': z_values}