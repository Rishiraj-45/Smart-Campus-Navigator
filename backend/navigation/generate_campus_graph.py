
from pathlib import Path
import html
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pprint import pformat


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAP_FILE = PROJECT_ROOT / "campus_map.drawio"
OUTPUT_FILE = Path(__file__).resolve().parent / "campus_map_data.py"


def clean_name(value):
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]*>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def location_type(name):
    upper = name.upper()

    if "STAIRS" in upper or "STAIRCASE" in upper:
        return "staircase"
    if "LIFT" in upper or "ELEVATOR" in upper:
        return "elevator"
    if "WASHROOM" in upper or "WAHROOM" in upper:
        return "washroom"
    if "LAB" in upper:
        return "laboratory"
    if "GATE" in upper or "ENTRANCE" in upper:
        return "entrance"
    if "FACULTY ROOM" in upper or "OFFICE" in upper:
        return "office"
    if "CAFETERIA" in upper or "MESS" in upper:
        return "food_service"
    if "BADMINTON" in upper or "GYM" in upper:
        return "sports_facility"
    if "INFORMATION DESK" in upper:
        return "information_desk"
    if "HALL" in upper or "ATRIUM" in upper:
        return "corridor"
    if "AUDITORIUM" in upper:
        return "auditorium"

    return "other"


def parse_drawio_file(path):
    """Read draw.io XML or XML embedded in a draw.io HTML export."""
    text = path.read_text(encoding="utf-8-sig")

    try:
        return ET.fromstring(text)
    except ET.ParseError:
        pass

    match = re.search(
        r'data-mxgraph="(.*?)"\s*></div>',
        text,
        re.S,
    )

    if not match:
        raise ValueError(
            "The file is not readable draw.io XML or an embedded "
            "draw.io HTML export."
        )

    config = json.loads(html.unescape(match.group(1)))
    return ET.fromstring(config["xml"])


def edge_distance_label(edge, cells_by_id):
    """Return an explicitly labelled distance; never estimate from geometry."""
    candidates = [edge.get("value", "")]

    for cell in cells_by_id.values():
        if cell.get("parent") == edge.get("id"):
            candidates.append(cell.get("value", ""))

    for candidate in candidates:
        value = clean_name(candidate)

        match = re.search(
            r"(?<!\w)(\d+(?:\.\d+)?)\s*(?:m|metres?|meters?)?\b",
            value,
            re.I,
        )

        if match:
            return float(match.group(1)), True

    return None, False


def main():
    if not MAP_FILE.exists():
        raise FileNotFoundError(
            f"Map not found: {MAP_FILE}\n"
            "Place campus_map.drawio in the project root."
        )

    root = parse_drawio_file(MAP_FILE)
    diagrams = root.findall("diagram")

    floors = []

    for floor_index, diagram in enumerate(diagrams):
        model = diagram.find("mxGraphModel")
        if model is None:
            continue

        graph_root = model.find("root")
        if graph_root is None:
            continue

        cells = list(graph_root.findall("mxCell"))
        cells_by_id = {
            cell.get("id"): cell
            for cell in cells
        }

        vertices = {
            cell.get("id"): cell
            for cell in cells
            if cell.get("vertex") == "1"
            and cell.get("parent") == "1"
        }

        edges = [
            cell for cell in cells
            if cell.get("edge") == "1"
        ]

        floors.append({
            "index": floor_index,
            "name": diagram.get("name", f"Floor {floor_index}"),
            "vertices": vertices,
            "edges": edges,
            "cells_by_id": cells_by_id,
        })

    if len(floors) != 2:
        raise ValueError(
            f"Expected 2 floor diagrams, found {len(floors)}."
        )

    # Collect labelled locations from both floors.
    entries = []

    for floor in floors:
        for cell_id, cell in floor["vertices"].items():
            label = clean_name(cell.get("value"))

            if label:
                entries.append({
                    "floor": floor["index"],
                    "floor_name": floor["name"],
                    "cell_id": cell_id,
                    "label": label,
                })

    # Create unique names, including duplicate labels on the same floor.
    label_counts = Counter(
        (item["floor"], item["label"].casefold())
        for item in entries
    )

    used_names = set()
    names_by_cell = {}

    for item in entries:
        label = item["label"]
        floor_index = item["floor"]
        floor_name = item["floor_name"]

        name = label

        if label_counts[(floor_index, label.casefold())] > 1:
            name = f"{label} ({floor_name})"

        base_name = name
        suffix = 2

        while name.casefold() in {
            existing.casefold() for existing in used_names
        }:
            name = f"{base_name} ({suffix})"
            suffix += 1

        used_names.add(name)
        names_by_cell[(floor_index, item["cell_id"])] = name

    locations = {}
    graph = {
        name: [] for name in names_by_cell.values()
    }

    edge_metadata = []
    skipped_edges = []
    pending_edges = []
    confirmed_edges = []

    for floor in floors:
        floor_index = floor["index"]
        cells_by_id = floor["cells_by_id"]

        for item in entries:
            if item["floor"] != floor_index:
                continue

            name = names_by_cell[
                (floor_index, item["cell_id"])
            ]
            kind = location_type(item["label"])

            locations[name] = {
                "id": (
                    f"floor_{floor_index}_"
                    + re.sub(
                        r"[^a-z0-9]+",
                        "_",
                        name.casefold(),
                    ).strip("_")
                ),
                "name": name,
                "type": kind,
                "building": "Academic Block",
                "floor": floor_index,
                # Provisional default; accessibility must be verified.
                "accessible": kind != "staircase",
            }

        for edge in floor["edges"]:
            source = names_by_cell.get(
                (floor_index, edge.get("source"))
            )
            target = names_by_cell.get(
                (floor_index, edge.get("target"))
            )

            if not source or not target:
                skipped_edges.append({
                    "floor": floor["name"],
                    "edge_id": edge.get("id"),
                    "source": edge.get("source"),
                    "target": edge.get("target"),
                    "reason": "Unknown or missing endpoint",
                })
                continue

            distance, confirmed = edge_distance_label(
                edge,
                cells_by_id,
            )

            if not confirmed:
                # Keep the edge for auditing, not route calculation.
                pending_edges.append(
                    (floor["name"], source, target)
                )

                edge_metadata.append({
                    "floor": floor["name"],
                    "source": source,
                    "target": target,
                    "distance_m": None,
                    "distance_is_estimate": True,
                    "status": "pending_verification",
                    "drawio_edge_id": edge.get("id"),
                })

                continue

            if distance is None or distance <= 0:
                skipped_edges.append({
                    "floor": floor["name"],
                    "edge_id": edge.get("id"),
                    "source": source,
                    "target": target,
                    "reason": f"Invalid distance: {distance}",
                })
                continue

            confirmed_edges.append(
                (floor["name"], source, target, distance)
            )

            # Only explicitly labelled, positive distances enter the graph.
            graph[source].append((target, distance))
            graph[target].append((source, distance))

            edge_metadata.append({
                "floor": floor["name"],
                "source": source,
                "target": target,
                "distance_m": distance,
                "distance_is_estimate": False,
                "status": "confirmed",
                "drawio_edge_id": edge.get("id"),
            })

    # Deduplicate neighbours while retaining the shortest confirmed edge.
    for source, neighbours in graph.items():
        best = {}

        for target, distance in neighbours:
            best[target] = min(
                distance,
                best.get(target, float("inf")),
            )

        graph[source] = sorted(best.items())

    if skipped_edges:
        print("\nConnections requiring structural review:")

        for edge in skipped_edges:
            print(" -", edge)

        raise ValueError(
            f"{len(skipped_edges)} connections have missing or invalid "
            "endpoints/distances. No graph file was generated. "
            "Review the messages above before regenerating."
        )

    output = (
        "# Generated from campus_map.drawio. Do not edit by hand.\n"
        "LOCATIONS = "
        + pformat(locations, sort_dicts=False, width=100)
        + "\n\n"
        "CAMPUS_GRAPH = "
        + pformat(graph, sort_dicts=False, width=100)
        + "\n\n"
        "EDGE_METADATA = "
        + pformat(edge_metadata, sort_dicts=False, width=100)
        + "\n"
    )

    OUTPUT_FILE.write_text(output, encoding="utf-8")

    print("\nMap import completed.")
    print(
        "Ground Floor locations:",
        sum(value["floor"] == 0 for value in locations.values()),
    )
    print(
        "First Floor locations:",
        sum(value["floor"] == 1 for value in locations.values()),
    )
    print("Total locations:", len(locations))
    print(
        "Unique two-way connections:",
        sum(len(neighbours) for neighbours in graph.values()) // 2,
    )
    print("Confirmed connections:", len(confirmed_edges))
    print("Pending distance verification:", len(pending_edges))
    print("Generated:", OUTPUT_FILE)

    if pending_edges:
        print("\nConnections excluded from route calculation:")

        for floor_name, source, target in pending_edges:
            print(f" - {floor_name}: {source} <-> {target}")


if __name__ == "__main__":
    main()
