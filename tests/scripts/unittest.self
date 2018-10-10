(|
    true_comparision = (||
        assert: [true is: true].
        assertNot: [true is: false].
        assertNot: [true is: nil].
    ).
    run_tests = (||
        true_comparision.
    )
|) run_tests