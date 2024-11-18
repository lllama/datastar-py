from itertools import chain

# Event Types
FRAGMENT = "datastar-fragment"
SIGNAL = "datastar-signal"
REMOVE = "datastar-remove"
REDIRECT = "datastar-redirect"
CONSOLE = "datastar-console"

# Merge modes
MORPH = "morph"
INNER = "inner"
OUTER = "outer"
PREPEND = "prepend"
APPEND = "append"
BEFORE = "before"
AFTER = "after"
UPSERT_ATTRIBUTES = "upsertAttributes"


class ServerSentEventGenerator:

    def _send(self, event_type, data_lines, event_id=None, retry_duration=1_000) -> str:

        prefix = []
        if event_id:
            prefix.append(f"id: {event_id}")

        prefix.append(f"event: {event_type}")

        if retry_duration:
            prefix.append(f"retry: {retry_duration}")

        data_lines.append("\n")

        return "\n".join(chain(prefix, data_lines))

    def merge_fragment(
        self,
        data,
        selector=None,
        merge_mode=None,
        settle_duration=None,
        use_view_transition=True,
        event_id=None,
        retry_duration=1_000,
    ):
        data_lines = []
        if merge_mode:
            data_lines.append(f"data: merge {merge_mode}")
        if selector:
            data_lines.append(f"data: selector {selector}")
        if use_view_transition:
            data_lines.append("data: useViewTransition true")
        else:
            data_lines.append("data: useViewTransition false")
        if settle_duration:
            data_lines.append(f"data: settle {settle_duration}")

        data_lines.extend(f"data: fragment {x}" for x in data.splitlines())

        return self._send(FRAGMENT, data_lines, event_id, retry_duration)

    def remove_fragments(
        self,
        selector,
        settle_duration=None,
        use_view_transition=True,
        event_id=None,
        retry_duration=1_000,
    ):
        data_lines = []
        if selector:
            data_lines.append(f"data: selector {selector}")
        if use_view_transition:
            data_lines.append("data: useViewTransition true")
        else:
            data_lines.append("data: useViewTransition false")
        if settle_duration:
            data_lines.append(f"data: settle {settle_duration}")

        return self._send(REMOVE, data_lines, event_id, retry_duration)

    def merge_store(self, data, event_id, only_if_missing=False, retry_duration=1_000):
        data_lines = []
        if only_if_missing:
            data_lines.append("data: onlyIfMissing true")

        data_lines.extend(f"data: {x}" for x in data.splitlines())

        return self._send(SIGNAL, data_lines, event_id, retry_duration)

    def remove_from_store(self, paths, event_id, retry_duration=1_000):
        data_lines = []

        data_lines.extend(f"data: {x}" for x in paths.splitlines())

        return self._send(REMOVE, data_lines, event_id, retry_duration)

    def redirect(self, url, event_id, retry_duration=1_000):
        data_lines = [f"data: url {url}"]

        return self._send(REDIRECT, data_lines, event_id, retry_duration)

    def console(self, mode, message, event_id, retry_duration=1_000):
        data_lines = [f"data: {mode} {message}"]

        return self._send(REDIRECT, data_lines, event_id, retry_duration)
