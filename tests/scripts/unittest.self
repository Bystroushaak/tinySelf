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

    init = (| universe_mirror |
        init_true.
        init_false.

        universe_mirror: primitives mirrorOn: universe.
        universe_mirror toSlot: 'assert:' Add: (| :what |
            what value ifFalse: [primitives interpreter halt: 'Assertion failed!'].
        ).
        universe_mirror toSlot: 'assertNot:' Add: (| :what |
            what value ifTrue: [primitives interpreter halt: 'Assertion failed!'].
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
    ).

    run_tests = (||
        true_comparision.
        false_comparision.
    )
|) run_tests.
