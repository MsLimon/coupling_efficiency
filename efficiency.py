# Script to calculate coupling efficiency
import numpy as np

# a = np.arange(15).reshape(3,5)
# b = np.array([2,3,4])

class Material:

    def __init__(self, name, n):

        self.name = name
        self.n = n
# Define the classes for the waveguide and the laser diode


class SquaredWaveguide:
    """
    A waveguide with a squared cross section.

    class input attributes
    ----------------------
    n_core: index of refraction of the waveguide's core.
    n_clad: index of refraction of the waveguide's cladding.
    core_thickness: thickness of the core layer. Units: um
    clad_thickness: thickness of the cladding layer. Units: um
    """
    def __init__(self, n_core, n_clad, core_thickness, clad_thickness):
        # TODO - check for validity and units.
        # basic parameters
        self.n_core = n_core
        self.n_clad = n_clad
        self.core_thickness = core_thickness
        self.clad_thickness = clad_thickness
        # calculate additional parameters
        self.theta = self.get_acceptance_angle() # acceptance angle

    def get_acceptance_angle(self):
        # calculate numerical aperture
        na = np.sqrt(self.n_core**2 - self.n_clad**2)
        # derive acceptance angle from numerical aperture
        theta = np.arcsin(na)
        return theta


class LaserDiode:
    """
    A laser diode object.

    class input attributes
    ----------------------
    Properties of the laser diode
    lda: wavelength.
    fwhm_slow: Full width at half maximum on the slow axis. Units: deg
    fwhm_fast: Full width at half maximum on the fast axis. Units: deg
    width: width of the emitting surface. Units: um
    height: height of the emitting surface. Units: um
    """

    def __init__(self, lda, fwhm_slow, fwhm_fast, width, height):
        # TODO - check for validity and units.
        self.lda = lda
        self.FWHM_slow = fwhm_slow
        self.FWHM_fast = fwhm_fast
        self.width = width
        self.height = height
        # calculate the emitting surface
        self.As = self.width * self.height
        self.l_coefficient = self.get_power_distribution_coefficient(self.FWHM_slow)
        self.t_coefficient = self.get_power_distribution_coefficient(self.FWHM_fast)

    def get_power_distribution_coefficient(self,fwhm):
        """
        Calculate power distribution coefficient. This coefficient is later used in the expression of the radiance
        of laser diode. (Can be used for both the parallel and perpendicular coefficients).

        :return:
        m: power distribution coefficient.
        """
        # change the unit of the fwhm angle from deg to rad
        fwhm_rad = np.deg2rad(fwhm)
        # calculate the coefficient
        m = np.log(0.5)/np.log(np.cos(fwhm_rad/2))
        # take the integer part
        m = np.floor(m)
        return m

class Calculator:
    """
    Calculate coupling efficiency.
    """
    def __init__(self, waveguide, laserdiode):
        self.wv = waveguide
        self.ld = laserdiode

    def geometrical_losses(self):
        """
        Calculate geometrical losses. Depending on the relative size of the emitting area of the laser diode and the
        cross-section of the waveguide.
        :return:
        n_geom: geometrical factor for coupling efficiency
        """
        # TODO - make a input parameter to select between but coupling and a separated source. Or make separation
        # the input parameter and make it 0 by default.

        # give shorter names to the useful variables
        wv_l = self.wv.core_thickness
        ld_w = self.ld.width
        ld_h = self.ld.height

        if wv_l >= ld_w and wv_l >= ld_h:
            # if the source dimensions are smaller than the dimension of the waveguide core area,
            # all the light will be couples into the fiber.
            n_geom = 1

        if wv_l < ld_w and wv_l < ld_h:
            # if the source is larger than the waveguide core area , the geometrical factor for coupling efficiency
            # is given by the ratio of light captured by the fiber. The ratio of the areas.
            n_geom = (wv_l ** 2) / (ld_h * ld_w)

        if wv_l < ld_w and wv_l >= ld_h:
            # if the waveguide core area is larger than one side of the source, but smaller than the second side.
            # The geometrical factor for coupling efficiency is given by the following ratio
            n_geom = wv_l / ld_w

        if wv_l >= ld_w and wv_l < ld_h:
            # if the waveguide core area is larger than one side of the source, but smaller than the second side.
            # The geometrical factor for coupling efficiency is given by the following ratio
            n_geom = wv_l / ld_h
        return n_geom

    def fresnel_losses(self):
        """
        Calculate Fresnel losses.
        :return:
        n_fresnel: Fresnel factor for coupling efficiency
        """
        # give shorter names to the useful variables
        n_core = self.wv.n_core
        r = (n_core - 1)**2 / (n_core + 1)**2
        n_fresnel = 1 - r
        return n_fresnel

    def angular_losses(self):
        """
        Calculate angular losses (due to the spatial distribution of the power emitted by the source).
        :return:
        """
        # get relevant parameters
        theta = self.wv.theta
        l = self.ld.l_coefficient
        t = self.ld.t_coefficient

        n_angular_l = 1 - (np.cos(theta)) ** (l + 1)
        n_angular_t = 1 - (np.cos(theta)) ** (t + 1)

        n_angular = np.sqrt(n_angular_l * n_angular_t)
        return n_angular