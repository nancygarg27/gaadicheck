from anomaly import analyze

def test_clean_car_has_no_flags():
    df = analyze(1) # 1 here is vehicle id
    assert not df["is_rollback"].any()
    assert not df["is_flatline"].any()
    assert not df["is_jump"].any()

