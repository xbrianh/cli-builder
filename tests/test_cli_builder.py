#!/usr/bin/env python
import os
import sys
import unittest
import argparse

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

import cli_builder


class TestXCLI(unittest.TestCase):
    def test_dispatch(self):
        with self.subTest("dispatch without mutually exclusive arguments"):
            self._test_dispatch()

        with self.subTest("dispatch with mutually exclusive arguments"):
            self._test_dispatch(mutually_exclusive=True)

        with self.subTest("dispatch with command overrides"):
            self._test_dispatch(command_overrides=True)

    def _test_dispatch(self, mutually_exclusive=None, command_overrides=False):
        dispatch = cli_builder.Dispatch()
        group = dispatch.group(
            "my_group",
            arguments={
                "foo": dict(default="george", type=int),
                "--argument-a": None,
                "--argument-b": dict(default="bar"),
            },
            mutually_exclusive=(["--argument-a", "--argument-b"] if mutually_exclusive else None)
        )

        if command_overrides:
            @group.command("my_command", arguments={"foo": None, "--bar": dict(default="bars")})
            def my_command(args):
                self.assertEqual(args.argument_b, "LSDKFJ")
                self.assertEqual(args.foo, "24")
                self.assertEqual(args.bar, "bars")
        else:
            @group.command("my_command")
            def my_command(args):
                self.assertEqual(args.argument_b, "LSDKFJ")
                self.assertEqual(args.foo, 24)

        dispatch(["my_group", "my_command", "24", "--argument-b", "LSDKFJ"])


if __name__ == '__main__':
    unittest.main()
