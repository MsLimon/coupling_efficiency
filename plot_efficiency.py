import efficiency as ef
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns


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
    waveguide1 = ef.SquaredWaveguide(1.51,1.465,50,1)
    waveguide2 = ef.SquaredWaveguide(1.51,1.465,30,1)
    # make a list of the lasers so that we can iterate over them
    waveguides = [waveguide1, waveguide2]

    theta_deg = np.rad2deg(waveguide1.theta)
    print(f"Waveguide's acceptance angle: theta = {theta_deg} deg")

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
    # laser1 = ef.LaserDiode(405,9,26,2,0.4)
    laser1 = ef.LaserDiode(405, 9, 26)
    # CHIP-980-P50 infrared
    laser2 = ef.LaserDiode(980,13,30)
    # 650nm Red Laser Diode Chips for DVD
    laser3 = ef.LaserDiode(655,8,28)
    # communications laser 1550nm wavelength
    laser4 = ef.LaserDiode(1550,9,28)

    # make a list of the lasers so that we can iterate over them
    lasers = [laser1, laser2, laser3, laser4]

    # generate a vector/array containing the separating distances between the LD and the WG to be evaluated
    x = np.arange(1,200,0.5)
    n = len(x)

    # create an empty list to store the labels of the plots for each laser
    labels = []

    # activate seaborn plotting
    sns.set()
    sns.set_style("whitegrid")
    # sns.set_palette()
    # sns.set_palette(sns.color_palette("GnBu_d"))

    # calculate the efficiency for each laser as well
    for waveguide in waveguides:
        for laser in lasers:
            # now we make an instance of the efficiency calculator. That is, we bring together the information of the laser
            # diode and the waveguide, so that the program can calculate the coupling efficiency
            calc = ef.Calculator(waveguide, laser)
            # preallocate vectors for each efficiency
            n_geom = np.zeros(n)
            n_fresnel = calc.fresnel_losses()
            n_angular = calc.angular_losses()
            n_total = np.zeros(n)

            for i in range(n):
                wo_s, wo_f = laser1.calculate_beam_width(x[i])

                n_geom[i] = calc.geometrical_losses(x[i])

                n_total[i] = calc.total_efficiency(x[i])

            # plot the total efficiency as a function of the separation distance
            plt.plot(x, n_total)
            #labels.append(f'lambda = %i nm' % laser.lda)
            labels.append(f'lambda = {laser.lda} nm, t = {waveguide.core_thickness} um')

    plt.xlabel('Separation distance / um')
    plt.ylabel('Total coupling efficiency')
   #plt.legend(['blue', 'infrared', 'red'], loc='best')
    plt.legend(labels, loc='best')


    plt.show()

