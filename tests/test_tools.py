import pytest

from vitess_rag.tools import create_vitess_tools


class FakeCollection:
    def get(self, include=None):
        return {
            "documents": [
                "Capture Flux -y -z",
                "Filter -z",
                "Guide -z",
                "Monitor mon1 -z -Z",
                "Monitor mon2 -y -z",
                "Monitor mon_brilliance -z -Z",
                "Writeout -z -Z",
                "Filter -Z",
                "Guide -Y -Z",
                "Guide -Z",
            ],
            
            "metadatas": [
                {
                    "module": "VITESS Module Capture Flux",
                    "row_command_option": "-y -z",
                    "row_parameter_unit": "center y center z [cm]",
                    "row_description": (
                        "for circular foil: center y (horizontal) and z (vertical) "
                        "of the foil"
                    ),
                },
                {
                    "module": "VITESS Module Filter",
                    "row_command_option": "-z",
                    "row_parameter_unit": "min. z [cm]",
                    "row_description": (
                        "lower bound of the filter range in vertical direction (height)"
                    ),
                },
                {
                    "module": "VITESS Module Guide",
                    "row_command_option": "-z",
                    "row_parameter_unit": "first absorption material",
                    "row_description": (
                        "Absorbpion material (see the table of absorption materials below) "
                        "in the inner (left) side of the channel, see from bender entrance "
                        "- left side. Active, if neutrons are transmit between channels: "
                        "Option -g1"
                    ),
                },
                {
                    "module": "VITESS Module Monitor",
                    "row_command_option": "-z, -Z",
                    "row_parameter_unit": "filter Z pos min, max",
                    "row_description": (
                        "minimal and maximal wavelength to be taken into account. "
                        "Only neutrons arriving in that range are considered in the evaluation"
                    ),
                },
                {
                    "module": "VITESS Module Monitor",
                    "row_command_option": "-y, -z",
                    "row_parameter_unit": "number of y-, z-bins",
                    "row_description": (
                        "Number of the monitor channels in horizontal and vertical direction resp."
                    ),
                },
                {
                    "module": "VITESS Module Monitor",
                    "row_command_option": "-z, -Z",
                    "row_parameter_unit": "low, up bound z-pos [cm]",
                    "row_description": (
                        "minimal and maximal vertical position"
                    ),
                },
                {
                    "module": "VITESS Module Writeout",
                    "row_command_option": "-z -Z",
                    "row_parameter_unit": "filter Z pos. min/max [cm]",
                    "row_description": (
                        "(optional) Only neutrons within the given vertical space range are read"
                    ),
                },
                {
                    "module": "VITESS Module Filter",
                    "row_command_option": "-Z",
                    "row_parameter_unit": "max. z [cm]",
                    "row_description": (
                        "upper bound of the filter range in vertical direction (height)"
                    ),
                },
                {
                    "module": "VITESS Module Guide",
                    "row_command_option": "-Y, -Z",
                    "row_parameter_unit": "Horizontal / vertical shape",
                    "row_description": (
                        "shape of the guide: constant, linear, curved, parabolic, elliptic, "
                        "from file, or curved+linear"
                    ),
                },
                {
                    "module": "VITESS Module Guide",
                    "row_command_option": "-Z",
                    "row_parameter_unit": "MCPL file",
                    "row_description": (
                        "filename for saving events of gamma and neutron generation caused by "
                        "absorption, scattering etc. of the neutrons treated in the simulation"
                    ),
                },   
            ],
        }


def get_option_tool(collection):
    tools = create_vitess_tools(collection)

    return next(
        tool for tool in tools
        if tool.name == "vitess_option_lookup"
    )


class ScopedCollection:
    def get(self, include=None):
        # Enough unrelated single-flag rows to push the requested shared row
        # out of the five returned chunks under the old ranking.
        metas = [
            {"module": "Monitor", "source_file": "monitor.md",
             "row_command_option": flag, "chunk_type": "table"}
            for flag in ("-m", "-M", "-e", "-E") for _ in range(6)
        ] + [
            {"module": "eval_elast", "source_file": "eval_elast.md",
             "row_command_option": flags, "chunk_type": "table"}
            for flags in ("-m -M", "-e -E")
        ]
        return {"documents": [str(meta) for meta in metas], "metadatas": metas}

    def query(self, **kwargs):
        raise AssertionError("An exact flag lookup must not need embeddings")


@pytest.mark.parametrize("flag", ["-m", "-M", "-e", "-E"])
def test_named_module_is_a_filter_even_when_its_row_has_multiple_flags(flag):
    result = get_option_tool(ScopedCollection()).invoke(
        {"query": f"What does option {flag} mean in module eval_elast?"}
    )

    assert "source_file: eval_elast.md" in result
    assert "source_file: monitor.md" not in result


def test_missing_flag_in_named_module_does_not_answer_from_another_module():
    result = get_option_tool(FakeCollection()).invoke(
        {"query": "What does option -Y mean in module filter?"}
    )

    assert result == "NO_RESULTS"


def test_unscoped_shared_flag_still_requests_a_module():
    result = get_option_tool(ScopedCollection()).invoke({"query": "What does -e mean?"})

    assert result.startswith("AMBIGUOUS_QUERY")
    assert "Monitor" in result and "eval_elast" in result


def test_option_lookup_finds_lowercase_z_inside_multi_option_rows():
    collection = FakeCollection()
    option_tool = get_option_tool(collection)

    result = option_tool.invoke({"query": "-z"})

    assert "VITESS Module Capture Flux" in result
    assert "VITESS Module Filter" in result
    assert "VITESS Module Guide" in result
    assert "VITESS Module Monitor" in result
    assert "VITESS Module Writeout" in result


def test_option_lookup_finds_uppercase_Z_inside_multi_option_rows():
    collection = FakeCollection()
    option_tool = get_option_tool(collection)

    result = option_tool.invoke({"query": "-Z"})

    assert "VITESS Module Filter" in result
    assert "VITESS Module Guide" in result
    assert "VITESS Module Monitor" in result
    assert "VITESS Module Writeout" in result
