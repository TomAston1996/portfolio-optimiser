from portfoliooptimiser.main import sum


def test_main_function() -> None:
    assert sum(1, 3) == 4
