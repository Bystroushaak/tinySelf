(|
    print_green: what = (||
        "[1;32m" print.
        what print.
        "[0m" print.
    ).
    print_green_ok = (|| print_green: "ok\n". ).

    test_cascading_operator = (| o. |
        "test_cascading_operator .. " print.

        o: (| state <- 0.
              addOne = (|| state: state + 1. ). |).

        assert: [ o state == 0 ].

        o addOne.

        assert: [o state == 1 ].

        o addOne;
          addOne.

        assert: [o state == 3 ].

        print_green_ok.
    ).

    test_primitive_true = (||
        "test_primitive_true .. " print.

        assert: [true is: true].
        assertNot: [true is: false].
        assertNot: [true is: nil].

        # test asBool
        assert: [(true asBool) is: true].

        print_green_ok.
    ).

    test_primitive_false = (||
        "test_primitive_false .. " print.

        assert: [false is: false].
        assertNot: [false is: true].
        assertNot: [false is: nil].

        # test asBool
        assert: [(false asBool) is: false].

        print_green_ok.
    ).

    test_primitive_nil = (||
        "test_primitive_nil .. " print.

        assert: [nil is: nil].
        assertNot: [nil is: true].
        assertNot: [nil is: false].

        # test asBool
        assert: [(nil asBool) is: false].

        print_green_ok.
    ).

    test_that_parameters_are_rw_slots = (| msg: x = (|| x: true. x. ) |
        "test_that_parameters_are_rw_slots .. " print.

        # see #63 for details
        assert: [(msg: false) is: true].

        print_green_ok.
    ).

    test_double_return_from_block = (| test = (|| true ifTrue: [ ^true ]. ^false) |
        "test_double_return_from_block .. " print.

        assert: [ test is: true. ].

        print_green_ok.
    ).

    test_while = (| i <- 0. |
        "test_while .. " print.

        # also test tail call optimization
        [ i < 100 ] whileTrue: [
        #'while test i < 100: ' print. i < 100 printLine.
            assert: [ primitives interpreter numberOfFrames < 10 ].
            i: i + 1.

            assertNot: [ i > 120 ].
        ].

        assert: [ i == 100 ].

        print_green_ok.
    ).

    test_run_script = (||
        "test_run_script .. " print.

        primitives interpreter runScript: 'tests/scripts/to_test_include.txt'.

        assert: [ run_script_flag == 1 ].
    ).

    test_run_script_invalid_obj = (| raised_error <- false. |
        "test_run_script_invalid_obj .. " print.

        primitives interpreter setErrorHandler: [:msg. :err_process |
           raised_error: true.
           primitives interpreter restoreProcess: err_process.
        ].
        primitives interpreter runScript: 1.

        ^raised_error.

        print_green_ok.
    ).

    test_run_script_invalid_path = (| raised_error <- false. |
        "test_run_script_invalid_path .. " print.

        primitives interpreter setErrorHandler: [:msg. :err_process |
           raised_error: true.
           primitives interpreter restoreProcess: err_process.
        ].
        primitives interpreter runScript: '/azgabash::--!'.

        ^raised_error.
    ).

    test_run_script_invalid_obj = (| raised_error <- false. |
        "test_run_script_invalid_obj .. " print.

        primitives interpreter setErrorHandler: [:msg. :err_process |
           raised_error: true.
           primitives interpreter restoreProcess: err_process.
        ].
        primitives interpreter runScript: 1.

        ^raised_error.
    ).

    test_eval = (| a <- 1. |
        "test_eval .. " print.

        assert: [
            (primitives interpreter evalMethodObj: "(|| 'okurka')") == "okurka"
        ].
        assert: [
            # test that multiple statements actually works, see #103
            (primitives interpreter evalMethodObj: "(|| a: a + 1. a: a + 1. a )") == 3.
        ].

        print_green_ok.
    ).

    test_do_not_understand = (| return_name. return_parameters. |
        "test_do_not_understand .. " print.

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

        print_green_ok.
    ).

    test_primitive_int = (| raised_error <- false. |
        "test_primitive_int .. " print.

        primitives interpreter setErrorHandler: [:msg. :err_process |
           raised_error: true.
           primitives interpreter restoreProcess: err_process.
        ].

        1 / 0.

        assert: [ raised_error ].

        print_green_ok.
    ).

    test_primitive_str = (||
        "test_primitive_str .. " print.

        assert: [ "asd" == "asd" ].
        assertNot: [ "asd" == "---" ].

        assert: [ "asd" startsWith: "as" ].
        assertNot: [ "asd" startsWith: "d" ].

        assert: [ "asd" endsWith: "sd" ].
        assertNot: [ "asd" endsWith: "a" ].

        assert: [ "asd" contains: "s" ].
        assertNot: [ "asd" contains: "x" ].

        print_green_ok.
    ).

    test_primitive_list = (| l. other. reversed. |
        "test_primitive_list .. " print.

        l: list clone.
        other: list clone.

        # test `at:` and `length`
        l append: 1.
        assert: [ (l at: 0) == 1 ].
        assert: [ (l length) == 1 ].

        # test `at:` and `at:Put:`
        l append: 2.
        assert: [ (l at: 1) == 2 ].
        l at: 0 Put: 0.
        assert: [ (l at: 0) == 0 ].

        other: primitives list clone.
        other append: 'a'.
        other append: 'b'.

        # test `extend:`
        l extend: other.
        assert: [ (l at: 0) == 0 ].
        assert: [ (l at: 1) == 2 ].
        assert: [ (l at: 2) == 'a' ].
        assert: [ (l at: 3) == 'b' ].

        # test `reversed`
        reversed: other reversed.
        assert: [ (reversed at: 0) == 'b' ].
        assert: [ (reversed at: 1) == 'a' ].

        # test `clear`
        l clear.
        other clear.

        # test `do:`
        other: 0.
        l clear;
            append: 1;
            append: 2.

        l do: [| :item |
            other: other + item.
        ].
        assert: [ other == 3 ].

        # test `==`
        l clear.
        other: list clone.

        l append: 1.
        l append: "s".

        other append: 1.
        other append: "s".

        assert: [ l == other ].

        # test also negation
        other at: 1 Put: "x".

        assertNot: [ l == other ].

        # test asBool
        l clear.
        assert: [ (l asBool) is: false ].

        l append: 1.
        assert: [ l asBool is: true ].

        print_green_ok.
    ).

    test_primitive_dict = (| d. custom_obj. another_obj. did_run. ret_fail. |
        "test_primitive_dict .. " print.

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

        print_green_ok.
    ).

    test_primitive_file = (| read_only_file. tmp_file. err_run <- false. |
        "test_primitive_file .. " print.

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

        print_green_ok.
    ).

    test_primitive_socket = (| socket |
        "test_primitive_socket .. " print.

        socket: primitives os socket open: "google.com" Port: 80.
        socket sendAll: "GET / HTTP/1.1\n".
        socket sendAll: "Host: google.com\n".
        socket sendAll: "\n".
        assert: [(socket recv: 4) == "HTTP" ].

        print_green_ok.
    ).

    test_primitive_mirror = (| obj. mirror. parent. |
        "test_primitive_mirror .. " print.

        obj: (| first. second. |).
        mirror: primitives mirrorOn: obj.

        assert: [(mirror listSlots at: 0) == "first"].
        assert: [(mirror listSlots at: 1) == "first:"].
        assert: [(mirror listSlots at: 2) == "second"].
        assert: [(mirror listSlots at: 3) == "second:"].

        parent: (| third = 1. |).
        mirror toParent: "p" Add: parent.

        assert: [ obj third == 1 ].

        assert: [(mirror listParents at: 0) == "p"].

        print_green_ok.
    ).

    run_tests = (||
        test_while.
        test_cascading_operator.
        test_primitive_true.
        test_primitive_false.
        test_primitive_nil.
        test_eval.
        test_do_not_understand.
        test_primitive_int.
        test_primitive_str.
        test_primitive_list.
        test_primitive_dict.
        test_primitive_file.
        test_primitive_socket.
        test_primitive_mirror.

        test_that_parameters_are_rw_slots.
        test_double_return_from_block.

        assert: [| rval |
            rval: test_run_script_invalid_obj is: true.
            print_green_ok.
            rval.
        ].
        assert: [| rval |
            rval: test_run_script_invalid_path is: true.
            print_green_ok.
            rval.
        ].
        test_run_script.

        assert: [ primitives time timestamp > 1546723901.1 ].
        assert: [ primitives interpreter scriptPath endsWith: "unittest.self" ].

        "All tests ok." printLine.
    )
|) run_tests.
