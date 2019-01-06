(|
    init_true = (| true_mirror |
        true_mirror: primitives mirrorOn: true.

        true_mirror toSlot: 'ifTrue:' Add: (| :blck | blck value).
        true_mirror toSlot: 'ifFalse:' Add: (| :blck | nil.).
        true_mirror toSlot: 'ifTrue:False:' Add: (| :true_blck. :false_blck |
            true_blck value
        ).
        true_mirror toSlot: 'ifFalse:True:' Add: (| :false_blck. :true_blck |
            true_blck value.
        ).
    ).
    init_false = (| false_mirror |
        false_mirror: primitives mirrorOn: false.

        false_mirror toSlot: 'ifTrue:' Add: (| :blck | nil).
        false_mirror toSlot: 'ifFalse:' Add: (| :blck | blck value.).
        false_mirror toSlot: 'ifTrue:False:' Add: (| :true_blck. :false_blck |
            false_blck value
        ).
        false_mirror toSlot: 'ifFalse:True:' Add: (| :false_blck. :true_blck |
            false_blck value.
        ).
    ).

    init = (| universe_mirror. block_traits_mirror |
        init_true.
        init_false.

        universe_mirror: primitives mirrorOn: universe.
        universe_mirror toSlot: 'assert:' Add: (| :what |
            what value ifFalse: [
                primitives interpreter error: (
                    '`assert:` failed (line ' + (what getLineNumber asString) + '):\n\n\t' + (what asString)
                )
            ].
        ).
        universe_mirror toSlot: 'assertNot:' Add: (| :what |
            what value ifTrue: [
                primitives interpreter error: (
                    '`assertNot:` failed (line ' + (what getLineNumber asString) + '):\n\n\t' + (what asString)
                )
            ].
        ).

        block_traits_mirror: primitives mirrorOn: block_traits.
        block_traits_mirror toSlot: 'whileTrue:' Add: (| :blck |
            self value ifFalse: [ ^nil ].
            blck value.
            ^self whileTrue: blck.
        ).
    ).
|) init.

(|
    true_comparision = (||
        assert: [true is: true].
        assertNot: [true is: false].
        assertNot: [true is: nil].
    ).

    false_comparision = (||
        assert: [false is: false].
        assertNot: [false is: true].
        assertNot: [false is: nil].
    ).

    nil_comparision = (||
        assert: [nil is: nil].
        assertNot: [nil is: true].
        assertNot: [nil is: false].
    ).

    test_that_parameters_are_rw_slots = (| msg: x = (|| x: true. x. ) |
        # see #63 for details
        assert: [(msg: false) is: true].
    ).

    test_double_return_from_block = (| test = (|| true ifTrue: [ ^true ]. ^false) |
        assert: [ test is: true. ].
    ).

    test_while = (| i <- 0. |
        [ i < 100 ] whileTrue: [
            assert: [ primitives interpreter numberOfFrames < 10 ].
            i: i + 1.
        ].

        assert: [ true ].
    ).

    test_run_script = (||
        primitives interpreter runScript: 'tests/scripts/to_test_include.txt'.

        assert: [ run_script_flag == 1 ].
    ).
    test_run_script_invalid_obj = (| raised_error <- false. |
        primitives interpreter setErrorHandler: [:obj. :stack |
           raised_error: true.
        ].
        primitives interpreter runScript: 1.

        assert: [raise_error is: True].
    ).

    test_run_script_invalid_obj = (| raised_error <- false. |
        primitives interpreter setErrorHandler: [:msg. :err_process |
           raised_error: true.
           primitives interpreter restoreProcess: err_process.
        ].
        primitives interpreter runScript: 1.

        ^raised_error.
    ).

    test_run_script_invalid_path = (| raised_error <- false. |
        primitives interpreter setErrorHandler: [:msg. :err_process |
           raised_error: true.
           primitives interpreter restoreProcess: err_process.
        ].
        primitives interpreter runScript: '/azgabash::--!'.

        ^raised_error.
    ).

    run_tests = (||
        true_comparision.
        false_comparision.
        nil_comparision.

        test_that_parameters_are_rw_slots.
        test_double_return_from_block.

        test_while.

        assert: [ test_run_script_invalid_obj is: true ].
        assert: [ test_run_script_invalid_path is: true ].
        test_run_script.

        assert: [ primitives time timestamp > 1546723901.1 ].

        "all tests ok\n" print.
    )
|) run_tests.
