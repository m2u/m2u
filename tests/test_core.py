import pytest

from m2u import core
from m2u import settings


def test_initialize(mocker):
    mocker.patch('core._init_program')
    mocker.patch('core._init_editor')
    mocker.patch('core._init_pipeline')
    core.initialize('test_program', 'test_editor')
    core._init_program.assert_called_once_with('test_program')
    core._init_editor.assert_called_once_with('test_editor')
    core._init_pipeline.assert_called_once()


def test_init_program_fail():
    with pytest.raises(ImportError):
        core._init_program('not_existing_program')


def test_init_editor_fail():
    with pytest.raises(ImportError):
        core._init_editor('not_existing_editor')


def test_init_pipeline_with_settings():
    raise NotImplementedError()
