# tests/test_pathmanager.py

import os
import tempfile
from pathlib import Path, PureWindowsPath, PurePosixPath

import pytest
import yaml

from o_pathmanager.formatter import PatternFormatter
from o_pathmanager.os_formatter import OSPathFormatter
from o_pathmanager.validator import TokenValidatorStrategy
from o_pathmanager.transformer import StringTransformerStrategy
from o_pathmanager.loader import YamlDeepMergeLoader
from o_pathmanager.manager import PathManager
from o_pathmanager.factory import PathManagerFactory


# -----------------------------------------------------------------------------
# PatternFormatter
# -----------------------------------------------------------------------------

def test_pattern_formatter_basic():
    fmt = PatternFormatter()
    pattern = "{a}/{b}"
    tokens = {"a": "foo", "b": "bar"}
    assert fmt.format(pattern, tokens) == "foo/bar"

def test_pattern_formatter_missing_key_raises_keyerror():
    fmt = PatternFormatter()
    with pytest.raises(KeyError):
        fmt.format("{x}/{y}", {"x": "only"})


# -----------------------------------------------------------------------------
# OSPathFormatter
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("os_name,filled,expected", [
    ("win",  "a/b/c.txt", PureWindowsPath("a", "b", "c.txt")),
    ("WIN",  "foo/bar",   PureWindowsPath("foo", "bar")),
    ("linux","one/two",   PurePosixPath("one", "two")),
    ("Mac",  "x/y/z",     PurePosixPath("x", "y", "z")),
])
def test_os_path_formatter_valid(os_name, filled, expected):
    fmt = OSPathFormatter()
    result = fmt.make_path(os_name, filled)
    assert result == expected

def test_os_path_formatter_unknown_os():
    fmt = OSPathFormatter()
    with pytest.raises(ValueError):
        fmt.make_path("solaris", "a/b")


# -----------------------------------------------------------------------------
# StringTransformerStrategy
# -----------------------------------------------------------------------------

def test_string_transformer_all_known():
    transformer = StringTransformerStrategy()
    tokens = {"name": "alice", "greet": "Hello"}
    transforms = {
        "name": ["uppercase"],
        "greet": ["lowercase", "capitalize"]
    }
    out = transformer.apply(transforms, tokens.copy())
    assert out["name"] == "ALICE"
    assert out["greet"] == "Hello"

def test_string_transformer_unknown_transform():
    transformer = StringTransformerStrategy()
    with pytest.raises(KeyError):
        transformer.apply({"foo": ["does_not_exist"]}, {"foo": "bar"})


# -----------------------------------------------------------------------------
# TokenValidatorStrategy
# -----------------------------------------------------------------------------

@pytest.fixture
def validator():
    return TokenValidatorStrategy()

def test_validator_valid_tokens(validator):
    tokens = {"rep": "abc_123_def", "descriptor": "temp", "layerID": "Z", "eye": "left"}
    tpl_conf = {"allowed_eyes": ["left", "right"]}
    validator.validate("t", tokens, tpl_conf)

@pytest.mark.parametrize("bad_rep", ["ABC_DEF_ghi", "a_b", "too_many_segments_here"])
def test_validator_invalid_rep(bad_rep, validator):
    with pytest.raises(ValueError):
        validator.validate("t", {"rep": bad_rep}, {})

def test_validator_invalid_descriptor(validator):
    with pytest.raises(ValueError):
        validator.validate("t", {"descriptor": "oops"}, {})

def test_validator_invalid_layerID(validator):
    with pytest.raises(ValueError):
        validator.validate("t", {"layerID": "AB"}, {})

def test_validator_eye_not_allowed(validator):
    with pytest.raises(ValueError):
        validator.validate("t", {"eye": "center"}, {"allowed_eyes": ["left", "right"]})


# -----------------------------------------------------------------------------
# YamlDeepMergeLoader
# -----------------------------------------------------------------------------

def write_yaml(path: Path, data: dict):
    path.write_text(yaml.safe_dump(data), encoding="utf-8")

def test_yaml_deep_merge_loader(tmp_path):
    studio = tmp_path / "studio.yaml"
    write_yaml(studio, {
        "templates": {
            "foo": {
                "pattern": "{a}/{b}",
                "required_tokens": ["a"],
                "optional_tokens": ["b"],
                "transforms": {"a": ["uppercase"]},
                "extras": {"x": 1}
            }
        }
    })
    override = tmp_path / "override.yaml"
    write_yaml(override, {
        "templates": {
            "foo": {
                "transforms": {"a": ["lowercase"], "b": ["capitalize"]},
                "extras": {"y": 2}
            },
            "bar": {
                "pattern": "{z}",
                "required_tokens": ["z"]
            }
        }
    })

    loader = YamlDeepMergeLoader()
    merged = loader.load([studio, override])

    assert merged["foo"]["transforms"]["a"] == ["uppercase", "lowercase"]
    assert merged["foo"]["transforms"]["b"] == ["capitalize"]
    assert merged["foo"]["extras"] == {"x": 1, "y": 2}
    assert "bar" in merged
    assert merged["bar"]["pattern"] == "{z}"


# -----------------------------------------------------------------------------
# PathManager
# -----------------------------------------------------------------------------

@pytest.fixture
def simple_templates(tmp_path):
    config = tmp_path / "cfg.yaml"
    write_yaml(config, {
        "templates": {
            "run": {
                "pattern": "{task}/{id}.dat",
                "required_tokens": ["task"],
                "optional_tokens": ["id"],
                "transforms": {"task": ["uppercase"]},
                "allowed_eyes": []
            }
        }
    })
    return config

def test_get_templates_is_copy(simple_templates):
    pm = PathManagerFactory.create_for_project(simple_templates, simple_templates)
    tpl1 = pm.get_templates()
    tpl1["run"]["pattern"] = "hacked"
    assert pm.get_templates()["run"]["pattern"] != "hacked"

def test_generate_minimal(tmp_path, simple_templates):
    pm = PathManager([simple_templates], default_os=None)
    out = pm.generate("run", {"task": "foo"})
    assert out == Path("FOO/.dat")

def test_generate_with_id_and_os(tmp_path, simple_templates):
    pm = PathManager([simple_templates], default_os="linux")
    tokens = {"task": "build", "id": "123"}
    result = pm.generate("run", tokens)
    assert result == PurePosixPath("BUILD", "123.dat")

def test_generate_missing_template(simple_templates):
    pm = PathManager([simple_templates])
    with pytest.raises(KeyError):
        pm.generate("nope", {})

def test_generate_missing_required(simple_templates):
    pm = PathManager([simple_templates])
    with pytest.raises(KeyError):
        pm.generate("run", {})

def test_generate_invalid_validator(tmp_path):
    config = tmp_path / "cfg2.yaml"
    write_yaml(config, {
        "templates": {
            "bad": {
                "pattern": "{rep}",
                "required_tokens": ["rep"],
                "transforms": {}
            }
        }
    })
    pm = PathManager([config])
    with pytest.raises(ValueError):
        pm.generate("bad", {"rep": "no_good"})


# -----------------------------------------------------------------------------
# PathManagerFactory
# -----------------------------------------------------------------------------

def test_factory_create_for_project(tmp_path, simple_templates):
    pm = PathManagerFactory.create_for_project(simple_templates, simple_templates, default_os="win")
    out = pm.generate("run", {"task": "x"})
    assert PureWindowsPath(out) == PureWindowsPath("X", ".dat")

def test_factory_create_for_show(tmp_path):
    studio = tmp_path / "std.yaml"
    override = tmp_path / "ProjectRoot" / "SHOW" / "configs" / "overrides.yaml"
    override.parent.mkdir(parents=True)
    write_yaml(studio, {"templates": {}})
    write_yaml(override, {"templates": {}})
    pm = PathManagerFactory.create_for_show(studio, tmp_path / "ProjectRoot", "SHOW", default_os=None)
    assert isinstance(pm.get_templates(), dict)
