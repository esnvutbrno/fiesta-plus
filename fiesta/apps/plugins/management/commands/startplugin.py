from pathlib import Path

from django.core.management.templates import TemplateCommand

PLUGINS_ROOT = Path(__file__).parent.parent.parent


class Command(TemplateCommand):
    help = (
        "Creates a Fiesta plugin app directory structure for the given plugin name in "
        "the current directory or optionally in the given directory."
    )
    missing_args_message = "You must provide an plugin name."

    def handle(self, **options):
        app_name = options.pop("name")

        target = options.pop("directory")
        if not target:
            target = PLUGINS_ROOT.parent / app_name
            target.mkdir()
            target = target.as_posix()

        options["template"] = (PLUGINS_ROOT / "plugin_template").as_posix()

        super().handle("plugin", app_name, target, **options)
