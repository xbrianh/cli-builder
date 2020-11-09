#!/usr/bin/env python
import io
import os
import sys
import unittest
import argparse
from typing import Optional

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

import cli_builder

from contextlib import contextmanager


class TestXCLI(unittest.TestCase):
    def test_dispatch(self):
        with self.subTest("dispatch without mutually exclusive arguments"):
            self._test_dispatch()

        with self.subTest("dispatch with mutually exclusive arguments"):
            self._test_dispatch(mutually_exclusive=True)

        with self.subTest("dispatch with command overrides"):
            self._test_dispatch(command_overrides=True)

        with self.subTest("Exception"):
            with self.assertRaises(SystemExit):
                self._test_dispatch(exception=Exception())

        with self.subTest("AttributeError"):
            with self.assertRaises(SystemExit):
                self._test_dispatch(exception=AttributeError())

    def test_error_reporting(self):
        exc_class = ValueError
        msg = "doom and gloom"
        with self.subTest("normal error reporting"):
            with captured_output() as (stdout, stderr):
                try:
                    self._test_dispatch(exception=exc_class(msg))
                except SystemExit:
                    pass
            err_msg = stderr.getvalue().strip()
            self.assertEqual(f"{exc_class.__name__}: {msg}", err_msg)
        with self.subTest("debug error reporting"):
            with captured_output() as (stdout, stderr):
                try:
                    self._test_dispatch(exception=exc_class(msg), debug=True)
                except SystemExit:
                    pass
            err_msg = stderr.getvalue().strip()
            self.assertNotEqual(f"{exc_class.__name__}: {msg}", err_msg)
            self.assertIn("Traceback", err_msg)

    def _test_dispatch(self,
                       mutually_exclusive=None,
                       command_overrides=False,
                       exception: Optional[Exception]=None,
                       debug: bool=False):
        dispatch = cli_builder.Dispatch(debug=debug)
        self.did_process_args = False

        def arg_proc(args: argparse.Namespace) -> argparse.Namespace:
            self.did_process_args = True
            return args

        group = dispatch.group(
            "my_group",
            arguments={
                "foo": dict(default="george", type=int),
                "--argument-a": None,
                "--argument-b": dict(default="bar"),
            },
            mutually_exclusive=(["--argument-a", "--argument-b"] if mutually_exclusive else None),
            arg_processor=arg_proc
        )

        if isinstance(exception, AttributeError):
            pass
        elif command_overrides:
            @group.command("my_command", arguments={"foo": None, "--bar": dict(default="bars")})
            def my_command(args):
                if exception is not None:
                    raise exception
                self.assertEqual(args.argument_b, "LSDKFJ")
                self.assertEqual(args.foo, "24")
                self.assertEqual(args.bar, "bars")
        else:
            @group.command("my_command")
            def my_command(args):
                if exception is not None:
                    raise exception
                self.assertEqual(args.argument_b, "LSDKFJ")
                self.assertEqual(args.foo, 24)

        dispatch(["my_group", "my_command", "24", "--argument-b", "LSDKFJ"])
        self.assertTrue(self.did_process_args)

@contextmanager
def captured_output():
    new_out, new_err = io.StringIO(), io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

if __name__ == '__main__':
    unittest.main()
