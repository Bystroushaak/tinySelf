(|
    true_comparision = (||
        assert: [true is: true]
        assertNot: [true is: false]
    )
|) run_tests