import numpy as np
from climlab import constants as const
from climlab.solar.insolation import daily_insolation
from climlab.solar.orbital import OrbitalTable
from climlab.model.ebm import EBM_seasonal
from climlab.solar.orbital_cycles import OrbitalCycles
from climlab.surface.albedo import StepFunctionAlbedo

# mostly copied from Insolation notebook
def test_daily_insolation():
    lat = np.linspace( -90., 90., 500. )
    days = np.linspace(0, const.days_per_year, 365. )
    Q = daily_insolation(lat, days)

    # check the range of Q
    np.testing.assert_almost_equal(Q.max(), 562.0333475)
    np.testing.assert_almost_equal(Q.min(), 0.0)

    # check the area integral
    Q_area_int = (np.sum(np.mean(Q, axis=1) * np.cos(np.deg2rad(lat))) /
                  np.sum(np.cos(np.deg2rad(lat))) )
    np.testing.assert_almost_equal(Q_area_int, 341.384184481)

def test_orbital_parameters():
    kyears = np.arange( -1000., 1.)
    table = OrbitalTable()
    orb = table.lookup_parameters(kyears)

    # check that orb has the right dictionary keys
    # key: (min, max)
    orb_expected = {'ecc': (0.004, 0.057),
                    'long_peri': (2.3, 360),
                    'obliquity': (22, 24.5) }

    for k in orb_expected:
        orb[k].min() > orb_expected[k][0]
        orb[k].max() > orb_expected[k][0]

#  Tests of automatic orbital cycles with EBM
def test_orbital_cycles():
    ebm = EBM_seasonal()
    print ebm
    #  add an albedo feedback
    albedo = StepFunctionAlbedo(state=ebm.state, **ebm.param)
    ebm.add_subprocess('albedo', albedo)
    #  run for 1,000 orbital years, but only 100 model years
    experiment = OrbitalCycles(ebm, kyear_start=-20, kyear_stop=-19,
                               orbital_year_factor=10.)
    assert experiment.orb_kyear == -20.
    np.testing.assert_almost_equal(experiment.T_segments_global, 11.48520525)
