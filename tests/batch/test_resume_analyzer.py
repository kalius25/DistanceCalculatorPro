from app.batch import ResumeAnalyzer, RouteJobStatus


def test_resume_analyzer_classifies_empty_existing_and_errors() -> None:
    analyzer = ResumeAnalyzer()

    empty = analyzer.analyze(None)
    assert empty.status is RouteJobStatus.PENDING
    assert not empty.should_skip
    assert not empty.has_result

    existing = analyzer.analyze("8.6 km")
    assert existing.status is RouteJobStatus.DONE
    assert existing.should_skip
    assert existing.distance_km == 8.6

    text = analyzer.analyze("Route completed")
    assert text.status is RouteJobStatus.DONE
    assert text.distance_km is None

    error = analyzer.analyze("ERROR: timeout")
    assert error.status is RouteJobStatus.PENDING
    assert error.reason == "previous_error"


def test_resume_analyzer_respects_disabled_skip_and_numeric_values() -> None:
    analyzer = ResumeAnalyzer()

    disabled = analyzer.analyze(12.5, skip_existing=False)
    assert disabled.status is RouteJobStatus.PENDING
    assert not disabled.should_skip
    assert disabled.has_result

    numeric = analyzer.analyze(12.5)
    assert numeric.distance_km == 12.5
    assert analyzer.analyze("1,25").distance_km == 1.25
    assert analyzer.analyze(True).distance_km is None
