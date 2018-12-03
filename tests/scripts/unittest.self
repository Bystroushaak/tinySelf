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
            what value ifFalse: [primitives interpreter error: 'Assertion failed!'].
        ).
        universe_mirror toSlot: 'assertNot:' Add: (| :what |
            what value ifTrue: [primitives interpreter error: 'Assertion failed!'].
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
        [ i < 500 ] whileTrue: [
            # 'i: ' print.
            # i asString print.
            # '\n' print.
            # 'number of frames: ' print.
            # primitives interpreter numberOfFrames asString print.
            # '\n\n' print.

            i: i + 1.
        ].

        assert: [ true ].
    ).

    run_tests = (||
        true_comparision.
        false_comparision.
        nil_comparision.

        test_that_parameters_are_rw_slots.
        test_double_return_from_block.

        test_while.

        "all tests ok\n" print.
    )
|) run_tests.
