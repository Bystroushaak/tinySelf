(|
    init_true = (| true_mirror |
        true_mirror: primitives mirrorOn: true.

        true_mirror toSlot: 'ifTrue:' Add: (| :blck | blck value).
        true_mirror toSlot: 'ifFalse:' Add: (| :blck | nil.).
    ).
    init_false = (| false_mirror |
        false_mirror: primitives mirrorOn: false.

        false_mirror toSlot: 'ifTrue:' Add: (| :blck | nil).
        false_mirror toSlot: 'ifFalse:' Add: (| :blck | blck value.).
    ).

    init = (| block_traits_mirror. |
        init_true.
        init_false.

        block_traits_mirror: primitives mirrorOn: block_traits.
        block_traits_mirror toSlot: 'whileTrue:' Add: (| :blck |
            self value ifFalse: [ ^nil ].
            blck value.
            ^self whileTrue: blck.
        ).
    ).

    test_while = (| i <- 0. |
        [ i < 50 ] whileTrue: [
            'i: ' print.
            i asString print.
            '\n' print.
            'number of frames: ' print.
            primitives interpreter numberOfFrames asString print.
            '\n\n' print.

            i: i + 1.
        ].
    ).
    test = (||
        init.
        test_while.
    ).
|) test.