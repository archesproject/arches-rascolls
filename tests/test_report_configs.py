import json
from pathlib import Path

from django.core import management
from django.test import TestCase

from arches.app.models.models import GraphModel
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import (
    import_graph as ResourceGraphImporter,
)

from arches_modular_reports.models import ReportConfig

PROJECT_ROOT = Path(__file__).parent.parent / "arches_rascolls"
RESOURCE_MODELS_DIR = PROJECT_ROOT / "pkg" / "graphs" / "resource_models"
REFERENCE_AND_SAMPLE_ITEM_GRAPH_FILE = (
    RESOURCE_MODELS_DIR / "Reference and Sample Collection Item.json"
)
# needed to validate the RelatedResourcesSection (Images) in search-item-details.json
DIGITAL_RESOURCES_GRAPH_FILE = RESOURCE_MODELS_DIR / "Digital Resources.json"
CONFIG_DIR = PROJECT_ROOT / "report_configs" / "reference_and_sample_collection_item"
ONTOLOGY_DIR = PROJECT_ROOT / "pkg" / "ontologies" / "linkedart"


class ReportConfigValidationTests(TestCase):
    """Guard against report configs drifting from the graph's node aliases.

    ReportConfig.clean() resolves every nodegroup_alias and node_alias in the
    config against the graph, so these tests fail when a model change renames
    or removes an alias that a report config still references.
    """

    @classmethod
    def setUpTestData(cls):
        management.call_command("load_ontology", source=str(ONTOLOGY_DIR), verbosity=0)
        cls.import_graph_file(REFERENCE_AND_SAMPLE_ITEM_GRAPH_FILE)
        cls.import_graph_file(DIGITAL_RESOURCES_GRAPH_FILE)
        cls.graph = GraphModel.objects.get(
            slug="reference_and_sample_collection_item", source_identifier=None
        )

    @staticmethod
    def import_graph_file(graph_file_path):
        with open(graph_file_path) as graph_file:
            archesfile = JSONDeserializer().deserialize(graph_file)
        for node in archesfile["graph"][0]["nodes"]:
            # branch publications aren't loaded in the test database
            node["sourcebranchpublication_id"] = None
        errors, _ = ResourceGraphImporter(archesfile["graph"], True)
        if errors:
            raise RuntimeError(f"Graph import failed: {errors}")

    def assert_config_aliases_resolve(self, filename):
        with open(CONFIG_DIR / filename) as config_file:
            config = json.load(config_file)
        ReportConfig(graph=self.graph, slug="test", config=config).clean()

    def test_default_report_config(self):
        self.assert_config_aliases_resolve("default.json")

    def test_search_item_details_config(self):
        self.assert_config_aliases_resolve("search-item-details.json")
