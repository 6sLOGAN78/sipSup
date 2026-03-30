"""The wake-word matcher is a pure function — so it gets deterministic evals.
Whisper mangles phrases in predictable ways; these cases pin the fuzziness."""

import pytest

from sipsup.gateway.voice import matches_wake

SHOULD_WAKE = [
    ("sipsup sipsup", "sipsup sipsup"),
    ("SipSup, sipsup!", "sipsup sipsup"),            # punctuation
    ("sipsupsipsup", "sipsup sipsup"),               # whisper drops the space
    ("so anyway sipsup sipsup schedule it", "sipsup sipsup"),  # embedded in speech
    ("walku sipsup", "sipsup sipsup"),             # one-letter mangle → fuzzy match
    ("Hey SipSup", "hey sipsup"),
    ("hey computer, what's up", "hey computer"),
    # regression from the first live session: whisper wrote the wake word in
    # kana — variants after a comma cover other scripts
    ("わくわく", "sipsup sipsup,わくわく"),
    ("わくわくわく", "sipsup sipsup,わくわく"),
    ("小助手你好", "sipsup sipsup,小助手"),
]

SHOULD_NOT_WAKE = [
    ("what a nice day", "sipsup sipsup"),
    ("wake up call at nine", "sipsup sipsup"),
    ("", "sipsup sipsup"),
    ("sipsup sipsup", ""),                        # no wake word configured
    ("walk to work", "sipsup sipsup"),
]


@pytest.mark.parametrize("heard,wake", SHOULD_WAKE, ids=[h for h, _ in SHOULD_WAKE])
def test_wakes(heard, wake):
    assert matches_wake(heard, wake)


@pytest.mark.parametrize("heard,wake", SHOULD_NOT_WAKE, ids=[h or "empty" for h, _ in SHOULD_NOT_WAKE])
def test_stays_asleep(heard, wake):
    assert not matches_wake(heard, wake)
