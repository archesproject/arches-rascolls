"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import sys, json, os
from arches.app.models.models import GraphModel
from arches_modular_reports.models import ReportConfig
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Command to build a custom report config from a report layout

    """

    section_definitions = None

    def add_arguments(self, parser):
        parser.add_argument(
            "graph",
            nargs="?",
            default="reference_and_sample_collection_item",
            help="graph slug",
        )

        parser.add_argument(
            "report_slug",
            nargs="?",
            default="default",
            help="report slug",
        )

        parser.add_argument(
            "-y",
            "--yes",
            action="store_true",
            dest="yes",
            help='used to force a yes answer to any user input "continue? y/n" prompt',
        )

    def handle(self, **options):
        if options["yes"] is False:
            response = input(
                "This will overwrite the report config in your database. Proceed? (Y/N): "
            )
            if response.lower() not in ("t", "true", "y", "yes"):
                exit()

        slug = options["graph"]
        report_slug = options["report_slug"]
        graphid = self.get_graph_id(slug)
        graph_config = self.get_config(graphid, report_slug)
        layout = self.get_layout(slug)
        updated_config = self.modify_config(graph_config, layout)
        ReportConfig.objects.filter(graph_id=graphid, slug=report_slug).update(
            config=updated_config
        )
        sys.stdout.write("Report config updated")

    def get_layout(self, graph):
        data = None
        layout_location = os.path.join(
            os.getcwd(),
            "arches_rascolls",
            "report_definitions",
            f"{graph}.json",
        )
        with open(layout_location, mode="r", encoding="utf-8") as f:
            data = json.loads(f.read())
        return data

    def get_graph_id(self, graph):
        graphid = None
        graph_instance = GraphModel.objects.filter(slug=graph).first()
        if graph_instance:
            graphid = graph_instance.pk
        else:
            sys.stderr.write("Not a valid graph id or slug")

        return graphid

    def get_config(self, graphid, slug):
        if graphid:
            try:
                return ReportConfig.objects.get(graph_id=graphid, slug=slug).config
            except:
                sys.stderr.write("No report config available for this graph")

    def build_nodegroups(self, components):
        nodegroups = []
        for component in components:
            print(component["nodes"])
            nodegroup = self.build_data_section(
                component["name"],
                component["nodegroup"],
                component["nodes"],
                component.get("filters", []),
            )
            nodegroups.append(nodegroup)
        return nodegroups

    def build_data_section(self, name, nodegroup, nodes, filters):
        return {
            "component": "arches_modular_reports/ModularReport/components/DataSection",
            "config": {
                "node_aliases": nodes,
                "custom_labels": {},
                "nodegroup_alias": nodegroup,
                "custom_card_name": name,
                "filters": filters,
            },
        }

    def build_sections(self, sections):
        return [
            {
                "component": "arches_rascolls/ModularReport/components/LinkedSections",
                "config": {
                    "sections": [
                        self.build_section(section, self.section_definitions[section])
                        for section in sections
                    ]
                },
            }
        ]

    def build_related_resources_section(self, graph_slug, node_aliases):
        return [
            {
                "component": "arches_modular_reports/ModularReport/components/RelatedResourcesSection",
                "config": {
                    "graph_slug": graph_slug,
                    "node_aliases": node_aliases,
                },
            }
        ]

    def build_section(self, name, section_def):
        return {
            "name": name,
            "components": self.build_nodegroups(section_def["components"]),
        }

    def build_tab(self, tab):
        return {"name": tab["name"], "components": self.build_sections(tab["sections"])}

    def modify_config(self, config, layout):
        self.section_definitions = layout["section_definitions"]
        for item in config["components"]:
            if item["component"].endswith("ReportHeader"):
                item["component"] = layout["header"]["component"]
                item["config"]["descriptor"] = layout["header"]["descriptor"]
            if item["component"].endswith("ReportTabs"):
                item["config"]["tabs"] = [self.build_tab(tab) for tab in layout["tabs"]]
        return config
