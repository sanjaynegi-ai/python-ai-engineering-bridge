"""Session 15, Milestone 4: the Streamlit UI, driven by Streamlit's AppTest. Do not edit.

AppTest runs ui.py as a script, in this process, without a browser. The UI builds its
assistant from the settings, so these tests point the settings at a private index with
the hashing embedder and the offline extractive generator: no download, no key.
"""

from pathlib import Path

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

UI = Path(__file__).parents[2] / "src" / "knowledge_assistant" / "ui.py"


@pytest.fixture
def ui_env(clean_env, docs, tmp_path, embedder):
    from knowledge_assistant.assistant import open_store
    from knowledge_assistant.ingestion import ingest
    from knowledge_assistant.settings import Settings

    clean_env.setenv("ASSISTANT_DOCUMENTS", str(docs))
    clean_env.setenv("ASSISTANT_INDEX", str(tmp_path / "index"))
    clean_env.setenv("ASSISTANT_EMBEDDER", "hashing")
    clean_env.setenv("ASSISTANT_GENERATOR", "extractive")
    settings = Settings()
    ingest(docs, open_store(settings, embedder), embedder)
    st.cache_resource.clear()  # don't reuse an assistant cached by another test
    yield clean_env
    st.cache_resource.clear()


def everything_shown(app: AppTest) -> str:
    """The text of every element on the page, in one string."""
    parts = []
    for kind in (
        "title",
        "header",
        "subheader",
        "markdown",
        "caption",
        "text",
        "info",
        "warning",
        "error",
        "success",
        "code",
    ):
        parts.extend(str(element.value) for element in getattr(app, kind))
    return "\n".join(parts)


def run_question(question: str) -> AppTest:
    app = AppTest.from_file(str(UI), default_timeout=60)
    app.run()
    [box] = [t for t in app.text_input if t.label == "Question"]
    box.input(question)
    [ask] = [b for b in app.button if b.label == "Ask"]
    ask.click()
    app.run()
    return app


def test_the_page_starts_with_a_question_box_and_no_answer(ui_env):
    app = AppTest.from_file(str(UI), default_timeout=60)
    app.run()
    assert not app.exception
    assert [t.label for t in app.text_input] == ["Question"]
    assert "Ask" in [b.label for b in app.button]
    assert "runbooks/" not in everything_shown(app)


def test_asking_shows_the_answer_and_its_sources(ui_env):
    app = run_question("How do I promote the orders database replica?")
    assert not app.exception
    shown = everything_shown(app)
    assert "[1]" in shown
    assert "runbooks/database-failover.md" in shown
    assert not app.error


def test_a_question_that_is_not_covered_says_so(ui_env):
    ui_env.setenv("ASSISTANT_MIN_SCORE", "1.0")  # nothing can be found
    st.cache_resource.clear()
    app = run_question("What's on the cafeteria menu?")
    assert not app.exception
    from knowledge_assistant.answering import NOT_FOUND

    assert NOT_FOUND in everything_shown(app)
    assert "runbooks/" not in everything_shown(app)


def test_a_blank_question_asks_for_a_question_without_failing(ui_env):
    app = run_question("   ")
    assert not app.exception
    assert app.warning or app.info


def test_the_assistant_is_built_once_not_on_every_rerun(ui_env, monkeypatch):
    import knowledge_assistant.assistant as assistant_module

    builds = []
    real_build = assistant_module.build_assistant

    def counting_build(*args, **kwargs):
        builds.append(1)
        return real_build(*args, **kwargs)

    monkeypatch.setattr(assistant_module, "build_assistant", counting_build)
    app = run_question("How do I promote the orders database replica?")
    [ask] = [b for b in app.button if b.label == "Ask"]
    ask.click()
    app.run()
    assert not app.exception
    assert len(builds) == 1  # Streamlit reran the script, but the assistant was cached


def test_an_index_built_with_other_settings_is_shown_as_an_error(ui_env):
    ui_env.setenv("ASSISTANT_CHUNK_SIZE", "300")  # the index was built with 800
    st.cache_resource.clear()
    app = run_question("How do I promote the orders database replica?")
    assert not app.exception
    assert app.error
    assert "chunk_size" in everything_shown(app)


def test_a_configuration_problem_is_shown_as_an_error_not_a_traceback(ui_env):
    ui_env.setenv("ASSISTANT_GENERATOR", "openai")  # and there's no OPENAI_API_KEY
    st.cache_resource.clear()
    app = run_question("How do I promote the orders database replica?")
    assert not app.exception
    assert app.error
    assert "OPENAI_API_KEY" in everything_shown(app)
