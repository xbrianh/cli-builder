# cli-builder: Decorators for building command group CLIs
cli-builder provides a user-friendly interface to quickly build up command group CLIs.

```
import cli_builder

dispatch = cli_builder.Dispatch()
my_cool_group = dispatch.group("my_cool_group")
my_other_cool_group = dispatch.group("my_other_cool_group")

@my_cool_group.command("do-stuff", arguments={
	"positional": dict(type=str),
	"--named": dict(type=int, default=5)
})
def my_func(args): 
	print(args.positional, args.named)

@my_cool_group.command("do-other-stuff", arguments=dict())
def my_other_func(args):
	pass

@my_other_cool_group.command("do-stuff-in-other-group")
def other_group_command(args):
	pass
```

## Installation
```
pip install cli-builder
```

## Links
Project home page [GitHub](https://github.com/xbrianh/cli-builder)  
Package distribution [PyPI](https://pypi.org/project/cli-builder/)

### Bugs
Please report bugs, issues, feature requests, etc. on [GitHub](https://github.com/xbrianh/cli-builder).
