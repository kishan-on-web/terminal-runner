import os
import subprocess
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

class TerminalExtension(Extension):
    def __init__(self):
        super(TerminalExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_argument()
        if not query:
            return [
                ExtensionResultItem(
                    icon='images/icon.png',
                    name="No command entered",
                    description="Please type a command to run.",
                    on_enter=None
                )
            ]

        return [
            ExtensionResultItem(
                icon='images/icon-white.png',
                name=f"Run Command: {query}",
                description="Press Enter to execute the command.",
                on_enter=ExtensionResultItem.Action(
                    name="execute_command",
                    data={"command": query}
                )
            )
        ]

class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        command = event.get_data().get("command")

        try:
            # Get the current working directory
            cwd = os.getcwd()

            # Run the command silently and capture output
            result = subprocess.run(command, cwd=cwd, shell=True, capture_output=True, text=True, check=True)

            # If the command is successful
            extension.logger.info("Command executed successfully")
            return extension.notify(
                f"✅ Command Successful:\n{result.stdout.strip() or 'No output'}"
            )

        except subprocess.CalledProcessError as e:
            # Open terminal if an error occurs
            subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"cd {cwd}; {command}; exec bash"])

            extension.logger.error("Command failed")
            return extension.notify(f"❌ Command Failed:\n{e.stderr.strip()}")

if __name__ == "__main__":
    TerminalExtension().run()
