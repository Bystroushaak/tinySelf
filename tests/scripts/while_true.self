(|
    init = (| block_traits_mirror. |
        block_traits_mirror: primitives mirrorOn: block_traits.
        block_traits_mirror toSlot: 'whileTrue:' Add: (| :blck |
            blck value.
            ^self whileTrue: blck.
        ).
    ).
    test_while = (| i <- 0. |
        [ i < 5 ] whileTrue: [
            'i: ' print.
            i asString print.
            '\n' print.

            i: i + 1.
        ].
    ).
    test = (||
        init.
        test_while.
    ).
|) test.