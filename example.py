import efficiency


if __name__ == '__main__':
    # create an instance of a waveguide with a square cross-section.

    # Waveguide parameters
    # --------------------
    # n_core: index of refraction of the waveguide's core.
    # n_clad: index of refraction of the waveguide's cladding.
    # core_thickness: thickness of the core layer. Units: um
    # clad_thickness: thickness of the cladding layer. Units: um

    # we create an instance of a a waveguide with a square cross-section which is stored in the variable waveguide1 by
    # waveguide1 = efficiency.SquaredWaveguide(n_core, n_clad, core_thickness, clad_thickness)

    #Here: a waveguide with core material AF32 glass (n=1.51) and cladding material SiO2 (n=1.465)
    waveguide1 = efficiency.SquaredWaveguide(1.51,1.465,50,1)

    # create an instance of a laser diode.

    # Laser parameters
    # --------------------
    # lda: wavelength.
    # fwhm_slow: Full width at half maximum on the slow axis. Units: deg
    # fwhm_fast: Full width at half maximum on the fast axis. Units: deg
    # width: width of the emitting surface. Units: um
    # height: height of the emitting surface. Units: um

    # we create an instance of a laser diode which is stored in the variable laser1 by
    # laser1 = efficiency.LaserDiode(lda, fwhm_slow, fwhm_fast, width, height)

    # Here: GNx blue laser diode
    laser1 = efficiency.LaserDiode(405,9,26,2,0.4)

    print(f"Power distribution coefficients: L = {laser1.l_coefficient} and T = {laser1.t_coefficient}")

    # now we make an instance of the efficiency calculator. That is, we bring together the information of the laser
    # diode and the waveguide, so that the program can calculate the coupling efficiency
    calc = efficiency.Calculator(waveguide1,laser1)

    # once we have the calculator instance we can calculate the coupling efficiency
    n_geom = calc.geometrical_losses()
    n_fresnel = calc.fresnel_losses()
    n_angular = calc.angular_losses()

    # print the results
    print(f"The geometrical factor for coupling efficiency is: {n_geom}")
    print(f"The Fresnel factor for coupling efficiency is: {n_fresnel}")
    print(f"The angular factor for coupling efficiency is: {n_angular}")