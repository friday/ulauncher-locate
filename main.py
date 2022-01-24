import logging
import subprocess
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenAction import OpenAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction

logger = logging.getLogger(__name__)
cmd = [
    'timeout', '5s',
    'ionice', '-c', '3',
    'locate', '--quiet', '--basename', '--nofollow', '--ignore-case'
]


class LocateExtension(Extension):
    def __init__(self):
        super(LocateExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, _):
        query = event.get_argument().strip()
        results = []

        if not query or len(query) < 3:
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='images/search.svg',
                    name='Keep typing your search criteria ...'
                )
            ])

        process = subprocess.Popen(cmd + [query], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        output, err = process.communicate()

        if err:
            logger.error(err)
        else:
            for path in output.decode().split('\n')[:15]:
                if path:
                    results.append(ExtensionSmallResultItem(
                        icon='images/search.svg',
                        name=path,
                        on_enter=OpenAction(path)
                    ))

        if results:
            return RenderResultListAction(results)

        return RenderResultListAction([ExtensionResultItem(
            icon='images/search.svg',
            name=f'Could not find any files matching "{query}"',
            on_enter=HideWindowAction())
        ])


if __name__ == '__main__':
    LocateExtension().run()
