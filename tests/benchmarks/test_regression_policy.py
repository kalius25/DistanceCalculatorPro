import pytest

from app.benchmarks import RegressionPolicy

pytestmark = pytest.mark.performance_regression


def test_regression_policy_defaults_and_validation() -> None:
    policy = RegressionPolicy()

    assert policy.maximum_runtime_regression_percent == 10.0

    with pytest.raises(ValueError, match="percentages"):
        RegressionPolicy(maximum_runtime_regression_percent=-1)
    with pytest.raises(ValueError, match="Autosave"):
        RegressionPolicy(autosave_tolerance=-1)
    with pytest.raises(ValueError, match="warning_fraction"):
        RegressionPolicy(warning_fraction=0)
    with pytest.raises(ValueError, match="warning_fraction"):
        RegressionPolicy(warning_fraction=1.1)
