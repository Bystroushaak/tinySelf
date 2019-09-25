(|
    test_while = (| i <- 0. |
        [ i < 500 ] whileTrue: [
            'i: ' print.
            i asString print.
            '\n' print.
            'number of frames: ' print.
            primitives interpreter numberOfFrames asString print.
            '\n\n' print.

            i: i + 1.
        ].
    ).
|) test_while.
