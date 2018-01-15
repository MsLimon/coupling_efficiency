# Definitions to calculate coupling efficiency
import numpy as np


class SquaredWaveguide(object):
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
        self.theta = self.get_acceptance_angle()  # acceptance angle

    def get_acceptance_angle(self):
        # calculate numerical aperture
        na = np.sqrt(self.n_core**2 - self.n_clad**2)
        # derive acceptance angle from numerical aperture
        theta = np.arcsin(na)  # theta is in rad
        return theta


class LaserDiode(object):
    """
    A laser diode object.

    class input attributes (Properties of the laser diode)
    ----------------------
    lda: wavelength. Units: nm
    fwhm_slow: Full width at half maximum on the slow axis. Units: deg
    fwhm_fast: Full width at half maximum on the fast axis. Units: deg
    width: width of the emitting surface. Units: um
    height: height of the emitting surface. Units: um
    """

    def __init__(self, lda, fwhm_slow, fwhm_fast):
        # TODO - check for validity and units.
        self.lda = lda
        self.FWHM_slow = fwhm_slow
        self.FWHM_fast = fwhm_fast
        # self.width = width
        # self.height = height
        # # calculate the emitting surface
        # self.As = self.width * self.height

        # calculate power distribution coefficients
        self.l_coefficient = self.get_power_distribution_coefficient(self.FWHM_slow)
        self.t_coefficient = self.get_power_distribution_coefficient(self.FWHM_fast)
        # calculate gaussian beam parameters: half divergence angle, minimum half width and Rayleigh range
        self.theta_slow, self.wo_slow, self.xo_slow = self.get_gaussian_beam_parameters(self.FWHM_slow)
        self.theta_fast, self.wo_fast, self.xo_fast = self.get_gaussian_beam_parameters(self.FWHM_fast)

    def get_power_distribution_coefficient(self, fwhm):
        """
        Calculate power distribution coefficient. This coefficient is later used in the expression of the radiance
        of laser diode. (Can be used for both the parallel and perpendicular coefficients). This calculation assumes
        that the radiance distribution is circularly symmetric.

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

    def get_gaussian_beam_parameters(self, fwhm):
        """
        Calculate the half divergence angle, the beam minimum half width and the Rayleigh range from the FWHM.

        :param:
        fwhm: Full width at half maximum
        :return:
        theta: half divergence angle of the gaussian beam.
        wo: beam minimum half width.
        xo: Rayleigh range.
        """
        # change the unit of the fwhm angle from deg to rad
        fwhm_rad = np.deg2rad(fwhm)
        # calculate half divergence angle
        theta = (np.sqrt(2) * fwhm_rad) / (2 * np.sqrt(np.log(2)))
        # change lambda from nm to um
        lda_um = self.lda * 1e-3
        # derive the other two parameters
        wo = lda_um / (np.pi * theta)
        xo = np.pi * wo ** 2 / lda_um
        return theta, wo, xo

    def calculate_beam_width(self, x):
        """
        Calculate the beam half width at a distance x from the origin. The half width is calculated for the slow and
        fast axis, w_slow and w_fast.

        :param:
        x: distance, with respect to the origin, when the beam half width is calculated
        :return:
        w_slow: beam half width at a distance x from the source for the slow axis
        w_fast: beam half width at a distance x from the source for the fast axis
        """
        w_slow = self.wo_slow * np.sqrt(1 + (x / self.xo_slow) ** 2)
        w_fast = self.wo_fast * np.sqrt(1 + (x / self.xo_fast) ** 2)
        return w_slow, w_fast


class Calculator(object):
    """
    Calculate coupling efficiency between a laser diode and a squared waveguide.

    class input attributes
    ----------------------
    waveguide: a SquareWaveguide object
    laserdiode: a LaserDiode object
    """

    def __init__(self, waveguide, laserdiode):
        # check that the inputs are instances of the SquaredWaveguide and LaserDiode classes
        if not isinstance(waveguide, SquaredWaveguide):
            raise TypeError("waveguide input must be a SquaredWaveguide object.")
        if not isinstance(laserdiode, LaserDiode):
            raise TypeError("laserdiode input must be a LaserDiode object.")

        self.wv = waveguide
        self.ld = laserdiode

    def geometrical_losses(self, x=0):
        """
        Calculate the geometrical coupling efficiency factor when the waveguide is separated from the laser diode
        by a distance of x.

        :param:
        x: distance of separation between the laser diode and the waveguide
        :return:
        n_geom: geometrical factor for coupling efficiency
        """

        # give shorter names to the useful variables
        wv_l = self.wv.core_thickness
        # calculate the area of the spot size at a distance x from the light source
        ld_w, ld_h = self.ld.calculate_beam_width(x)
        # Note that the beam has an elliptical shape. Therefore, the area is given by pi*a*b,
        # where a and b are the ellipse semi axis.
        ld_A = np.pi * ld_h * ld_w

        # initialize the value of n_geom
        n_geom = 0

        if wv_l >= ld_w and wv_l >= ld_h:
            # if the source dimensions are smaller than the dimension of the waveguide core area,
            # all the light will be coupled into the fiber.
            n_geom = 1

        elif wv_l < ld_w and wv_l < ld_h:
            # if the source is larger than the waveguide core area, the geometrical factor for coupling efficiency
            # is given by the ratio of light captured by the fiber, i.e. the ratio of the areas.
            n_geom = (wv_l ** 2) / ld_A

        elif wv_l < ld_w and wv_l >= ld_h:
            # if the waveguide core area is larger than one side of the source, but smaller than the second side.
            # The geometrical factor for coupling efficiency is given by the following ratio
            n_geom = wv_l / ld_w

        elif wv_l >= ld_w and wv_l < ld_h:
            # if the waveguide core area is larger than one side of the source, but smaller than the second side.
            # The geometrical factor for coupling efficiency is given by the following ratio
            n_geom = wv_l / ld_h

        return n_geom

    def fresnel_losses(self):
        """
        Calculate Fresnel coupling efficiency factor.

        :return:
        n_fresnel: Fresnel factor for coupling efficiency
        """
        # give shorter names to the useful variables
        n_core = self.wv.n_core
        # calculate power reflectance
        r = (n_core - 1)**2 / (n_core + 1)**2
        n_fresnel = 1 - r
        return n_fresnel

    def angular_losses(self):
        """
        Calculate angular coupling efficiency factor
        (due to the spatial distribution of the power emitted by the source).

        :return:
        """
        # get relevant parameters
        theta = self.wv.theta
        k = self.ld.l_coefficient
        t = self.ld.t_coefficient

        # calculate the angular coupling for each perpendicular direction separately (assuming circular symmetry)
        n_angular_l = 1 - (np.cos(theta)) ** (k + 1)
        n_angular_t = 1 - (np.cos(theta)) ** (t + 1)
        # approximate the total angular efficiency factor by multiplying the square roots of each individual factor.
        n_angular = np.sqrt(n_angular_l * n_angular_t)
        return n_angular

    def total_efficiency(self, x):
        """
        Calculate the total efficiency for a separation between the laser diode and the waveguide of x.
        Multiplies the results of the geometrical, fresnel and angular efficiency factors.

        :param:
        x: distance of separation between the laser diode and the waveguide
        :return:
        n_total: coupling efficiency
        """
        n_geom = self.geometrical_losses(x)
        n_fresnel = self.fresnel_losses()
        n_angular = self.angular_losses()
        n_total = n_geom * n_fresnel * n_angular
        return n_total