"""Unit tests of the model mechanics (run with `python -m pytest`)."""
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rrm import Params, simulate
from rrm.scenarios import day, days, CALM, STREAM


def test_rates_stay_positive():
    s = simulate(days(day([(600, 60)]), day()), Params(), n_seeds=4)
    assert (s["mu1"] > 0).all() and (s["mu2"] > 0).all()


def test_deterministic_given_seed():
    a = simulate(day(), Params(), n_seeds=2, seed=7)["mu1"]
    b = simulate(day(), Params(), n_seeds=2, seed=7)["mu1"]
    assert np.array_equal(a, b)


def test_habitual_never_receives_observed_rate():
    # with w2 = 0 the habitual expectation cannot move, whatever the stream delivers
    s = simulate(day([(600, 120)]), Params(w2=0.0), n_seeds=2, mu1_0=1.0, mu2_0=1.0)
    assert np.allclose(s["mu2"], 1.0)


def test_without_downward_prediction_current_tracks_constant_rate():
    lam = np.full(2000, CALM)
    s = simulate(lam, Params(w_down0=0.0), noise=False, n_seeds=1, mu1_0=2.0, mu2_0=2.0)
    assert abs(s["mu1"][0, -1] - CALM) < 1e-3


def test_downward_prediction_pulls_towards_habitual():
    lam = np.full(3000, CALM)
    s = simulate(lam, Params(w2=0.0), noise=False, n_seeds=1, mu1_0=CALM, mu2_0=2.0)
    assert CALM < s["mu1"][0, -1] < 2.0


def test_entering_stream_is_surprising():
    lam = np.r_[np.full(300, CALM), np.full(10, STREAM)]
    s = simulate(lam, Params(), noise=False, n_seeds=1, mu1_0=CALM, mu2_0=CALM)
    assert s["w1"][0, 300] == Params().w1_high


def test_surprising_decrease_is_revised_slowly():
    # leaving a dense stream is surprising, but decreases never trigger fast revision
    lam = np.r_[np.full(30, STREAM), np.full(30, CALM)]
    s = simulate(lam, Params(), noise=False, n_seeds=1, mu1_0=STREAM, mu2_0=1.0)
    assert (s["w1"][0, 30:] == Params().w1_low).all()


def test_denser_stream_does_not_shorten_after_effect():
    def fall(rate):
        lam = np.r_[np.full(120, CALM), np.full(10, rate), np.full(200, CALM)]
        m = simulate(lam, Params(), noise=False, n_seeds=1, mu1_0=CALM, mu2_0=CALM)["mu1"][0, 130:] - CALM
        return int(np.argmax(m < m[0] / np.e))
    assert fall(32.0) >= 0.8 * fall(8.0)


def test_negative_errors_never_get_fast_revision():
    # after a short session, noisy negative errors must still be revised slowly
    lam = np.r_[np.full(120, CALM), np.full(2, STREAM), np.full(60, CALM)]
    s = simulate(lam, Params(), n_seeds=512, mu1_0=CALM, mu2_0=CALM)
    prev = np.c_[np.full((512, 1), CALM), s["mu1"][:, :-1]]
    assert not ((s["w1"] == Params().w1_high) & (s["R"] < prev)).any()
