# Just simple benchmark file to quickly measure, whether the optimization had
# any effect or not.

(|
    benchmark = (| i <- 0. |
        [i < 1000000] whileTrue: [
            i: i + 1.
        ].
    ).

    run_benchmark = (| start_time. end_time. |
        start_time: primitives time timestamp.
        benchmark.
        end_time: primitives time timestamp.

        end_time - start_time asString + '\n' print.
    ).
|) run_benchmark.
