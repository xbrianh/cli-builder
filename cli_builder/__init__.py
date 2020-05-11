"""
Provide an interface to build a command group CLI.

Commands are defined in groups. Arguments defined for a group will be available to all commands in that group.

Example:
```
dispatch = Dispatch()

my_cli_group = dispatch.group("my-group-name")

@my_cli_group.command("my-cool-command", arguments={
    "path": dict(help="location of VCF, either local, gs://path, or drs://path"),
    "--billing-project": dict(type=str, required=False)
})
def my_cool_command_handler(args):
    pass
```
"""
import os
import json
import typing
import argparse
import traceback


class _group:
    def __init__(self, group_name, dispatcher):
        self.group_name = group_name
        self.dispatcher = dispatcher

    def command(self, name: str, *, arguments: dict=None, mutually_exclusive: list=None):
        dispatcher = self.dispatcher
        arguments = arguments or dict()
        if mutually_exclusive is None:
            mutually_exclusive = dispatcher.groups[self.group_name]['mutually_exclusive'] or list()

        def register_command(func):
            parser = dispatcher.groups[self.group_name]['subparser'].add_parser(
                name,
                description=func.__doc__,
                formatter_class=argparse.RawDescriptionHelpFormatter
            )
            command_arguments = dispatcher.groups[self.group_name]['arguments'].copy()
            command_arguments.update(arguments)
            for argname, kwargs in command_arguments.items():
                if argname not in mutually_exclusive:
                    parser.add_argument(argname, **(kwargs or dict()))
            if mutually_exclusive:
                group = parser.add_mutually_exclusive_group(required=True)
                for argname in mutually_exclusive:
                    kwargs = command_arguments.get(argname) or dict()
                    group.add_argument(argname, **kwargs)
            parser.set_defaults(func=func)
            dispatcher.commands[func] = dict(group=dispatcher.groups[self.group_name], name=name)
            return func
        return register_command


class Dispatch:
    groups: dict = dict()
    commands: dict = dict()

    def __init__(self, description=None):
        description = description or self.__doc__
        self.parser = argparse.ArgumentParser(description=description,
                                              formatter_class=argparse.RawDescriptionHelpFormatter)
        self.parser_groups = self.parser.add_subparsers()

    def group(self, name: str, *, arguments: dict=None, mutually_exclusive: list=None, help=None):
        arguments = arguments or dict()
        group = self.parser_groups.add_parser(name, help=help)
        self.groups[name] = dict(subparser=group.add_subparsers(),
                                 arguments=arguments,
                                 mutually_exclusive=mutually_exclusive)
        return _group(name, self)

    def __call__(self, argv):
        args = self.parser.parse_args(argv)
        try:
            command = args.func
            try:
                command(args)
            except Exception:
                print(traceback.format_exc())
        except SystemExit:
            pass
        except AttributeError:
            args = self.parser.parse_args(argv[:1] + ["--help"])
            args.func(args)
