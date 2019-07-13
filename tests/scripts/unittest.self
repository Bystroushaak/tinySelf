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
            true.
        ).
        universe_mirror toSlot: 'assertNot:' Add: (| :what |
            what value ifTrue: [
                primitives interpreter error: (
                    '`assertNot:` failed (line ' + (what getLineNumber asString) + '):\n\n\t' + (what asString)
                )
            ].
            true.
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
        # also test tail call optimization
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

    test_eval = (| a <- 1. |
        assert: [
            (primitives interpreter evalMethodObj: "(|| 'okurka')") == "okurka"
        ].
        assert: [
            # test that multiple statements actually works, see #103
            (primitives interpreter evalMethodObj: "(|| a: a + 1. a: a + 1. a )") == 3.
        ].
    ).

    test_do_not_understand = (| return_name. return_parameters. |
        return_name: (|
            doNotUnderstand: msg Parameters: p = (|| msg. ).
        |).

        assert: [ return_name asd == "asd" ].
        assert: [ (return_name asd: 1 With: 2) == "asd:With:" ].

        return_parameters: (|
            doNotUnderstand: msg Parameters: p = (|| p. ).
        |).

        assert: [ return_parameters asd length == 0 ].
        assert: [ (return_parameters + 1) length == 1 ].
        assert: [| params. |
            params: (return_parameters asd: 1 With: 2).
            assert: [ (params at: 0) == 1 ].
            assert: [ (params at: 1) == 2 ].
        ].
    ).

    test_run_script_invalid_obj = (| raised_error <- false. |
        primitives interpreter setErrorHandler: [:msg. :err_process |
           raised_error: true.
           primitives interpreter restoreProcess: err_process.
        ].
        primitives interpreter runScript: 1.

        ^raised_error.
    ).

    test_primitive_int = (| raised_error <- false. |
        primitives interpreter setErrorHandler: [:msg. :err_process |
           raised_error: true.
           primitives interpreter restoreProcess: err_process.
        ].

        1 / 0.

        assert: [ raised_error ].
    ).

    test_primitive_str = (||
        assert: [ "asd" == "asd" ].
        assertNot: [ "asd" == "---" ].

        assert: [ "asd" startsWith: "as" ].
        assertNot: [ "asd" startsWith: "d" ].

        assert: [ "asd" endsWith: "sd" ].
        assertNot: [ "asd" endsWith: "a" ].

        assert: [ "asd" contains: "s" ].
        assertNot: [ "asd" contains: "x" ].
    ).

    test_primitive_list = (| l. other. reversed. |
        l: primitives list clone.
        l append: 1.
        assert: [ (l at: 0) == 1 ].
        assert: [ (l length) == 1 ].

        l append: 2.
        assert: [ (l at: 1) == 2 ].
        l at: 0 Put: 0.
        assert: [ (l at: 0) == 0 ].

        other: primitives list clone.
        other append: 'a'.
        other append: 'b'.

        l extend: other.
        assert: [ (l at: 0) == 0 ].
        assert: [ (l at: 1) == 2 ].
        assert: [ (l at: 2) == 'a' ].
        assert: [ (l at: 3) == 'b' ].

        reversed: other reversed.
        assert: [ (reversed at: 0) == 'b' ].
        assert: [ (reversed at: 1) == 'a' ].
    ).

    test_primitive_dict = (| d. custom_obj. another_obj. did_run. ret_fail. |
        d: primitives dict clone.
        d at: 1 Put: "X".
        assert: [ (d at: 1) == "X" ].
        assert: [ (d at: 2) == nil ].

        custom_obj: (|
            name = "first".
            val = 1.
            == o = (||
                did_run: true.
                val == (o val)
            ).
        |).
        d at: custom_obj Put: 1.

        another_obj: (|
            name = "second".
            val = 2.
            == obj = (||
                did_run: true.
                val == (obj val)
            ).
        |).
        d at: another_obj Put: 2.

        assert: [ (d at: custom_obj) == 1. ].
        assert: [ did_run is: true ].

        ret_fail: false.
        d at: 9999 Fail: [ ret_fail: true ].
        assert: [ ret_fail is: true ].
        assert: [ (d at: 2222 Fail: [ 1 ]) == 1 ].

        # test custom hash
        d: primitives dict clone.

        did_run: false.
        custom_obj: (|
            val = 1.
            hash = (|| did_run: true. ^1 ).
            == o = (|| ^ val == (o val)).
        |).
        d at: custom_obj Put: 1.

        assert: [ did_run is: true ].
    ).

    test_primitive_file = (| read_only_file. tmp_file. err_run <- false. |
        read_only_file: primitives os files open: "/dev/null".

        primitives os files open: "/-1blehhhhhh" Fails: [err_run: true].
        assert: [ err_run is: true ].
        err_run: false.

        tmp_file: primitives os files open: "/tmp/asdhahsd" Mode: "w" Fails: [
            err_run: true
        ].
        assert: [ err_run is: false ].
        tmp_file write: "azgabash".
        tmp_file close.

        tmp_file: primitives os files open: "/tmp/asdhahsd".
        assert: [ (tmp_file read) == "azgabash" ].
        tmp_file seek: 0.
        assert: [ (tmp_file read: 2) == "az" ].
        assert: [ tmp_file closed? is: false ].
        tmp_file close.
        assert: [ tmp_file closed? is: true ].
    ).

    test_primitive_socket = (| socket |
        socket: primitives os socket open: "google.com" Port: 80.
        socket sendAll: "GET / HTTP/1.1\n".
        socket sendAll: "Host: google.com\n".
        socket sendAll: "\n".
        assert: [(socket recv: 4) == "HTTP" ].
    ).

    run_tests = (||
        true_comparision.
        false_comparision.
        nil_comparision.
        test_eval.
        test_do_not_understand.
        test_primitive_int.
        test_primitive_str.
        test_primitive_list.
        test_primitive_dict.
        test_primitive_file.
        test_primitive_socket.

        test_that_parameters_are_rw_slots.
        test_double_return_from_block.

        test_while.

        assert: [ test_run_script_invalid_obj is: true ].
        assert: [ test_run_script_invalid_path is: true ].
        test_run_script.

        assert: [ primitives time timestamp > 1546723901.1 ].
        assert: [ primitives interpreter scriptPath endsWith: "unittest.self" ].

        "All tests ok." printLine.
    )
|) run_tests.
