import numpy as np
from ektelo.client.inference import get_A
from ektelo.client.inference import get_y
from ektelo.client.inference import LeastSquares
from ektelo.client.inference import NonNegativeLeastSquares
from ektelo.client.inference import MultiplicativeWeights
from ektelo.client.inference import AHPThresholding
from ektelo.client.measurement import laplace_scale_factor
from ektelo.private.measurement import Laplace
import unittest


class TestInference(unittest.TestCase):

    def setUp(self):
        self.n = 8
        self.eps_share = 0.1
        self.prng = np.random.RandomState(10)
        self.A = np.eye(self.n)
        self.X = np.random.rand(self.n)

    def test_get_A(self):
        y = Laplace(self.A, self.eps_share).measure(self.X, self.prng)
        noise_scales = [laplace_scale_factor(self.A, self.eps_share)] * len(y)

        np.testing.assert_array_equal(np.array(noise_scales), 
                                      1 / np.diag(get_A(self.A, noise_scales)))

    def test_get_y(self):
        y = Laplace(self.A, self.eps_share).measure(self.X, self.prng)
        noise_scales = [laplace_scale_factor(self.A, self.eps_share)] * len(y)

        np.testing.assert_array_equal(np.diag(y * get_A(self.A, noise_scales)),
                                      get_y(y, noise_scales).flatten())

    def test_client_interaction_LS(self):
        laplace = Laplace(self.A, self.eps_share)
        ans = laplace.measure(self.X, self.prng)
        least_squares = LeastSquares()
        x_est = least_squares.infer(self.A, ans)

        self.assertEqual(self.X.shape, x_est.shape)

    def test_client_interaction_NLS(self):
        laplace = Laplace(self.A, self.eps_share)
        ans = laplace.measure(self.X, self.prng)

        non_neg_least_squares = NonNegativeLeastSquares()
        x_est = non_neg_least_squares.infer(self.A, ans)
        self.assertEqual(self.X.shape, x_est.shape)

    def test_client_interaction_MW(self):
        laplace = Laplace(self.A, self.eps_share)
        ans = laplace.measure(self.X, self.prng)
        x_est_init = np.random.rand(self.n)

        mult_weight = MultiplicativeWeights()
        x_est = mult_weight.infer(self.A, ans, x_est_init)
        self.assertEqual(self.X.shape, x_est.shape)

    def test_client_interaction_HR(self):
        laplace = Laplace(self.A, self.eps_share)
        ans = laplace.measure(self.X, self.prng)
        eps_par = 0.1
        eta = 0.35
        ratio = 0.85

        AHP_threshold = AHPThresholding(eta, ratio)
        x_est = AHP_threshold.infer(self.A, ans, eps_par)
        self.assertEqual(self.X.shape, x_est.shape)

if __name__ == '__main__':
    unittest.main()
