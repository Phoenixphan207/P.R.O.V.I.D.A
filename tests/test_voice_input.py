from provida.infrastructure.voice_input import VoiceInput


def test_voice_does_not_start_during_construction():
    voice = VoiceInput("C:/missing-model")
    assert not voice.running
    assert not voice.available
