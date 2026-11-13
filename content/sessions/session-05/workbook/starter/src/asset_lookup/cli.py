"""Command-line entry point: `asset-lookup`.

    asset-lookup show ASSET_ID
    asset-lookup list [--team TEAM]
    asset-lookup note ASSET_ID TEXT [--ticket TICKET_ID]

Exit codes:
    0  success
    1  the asset was not found, or the service gave an unusable answer
    2  configuration or usage problem
    3  the service is unavailable, or refused the token
"""

import argparse
import sys

from asset_lookup.client import InventoryClient
from asset_lookup.errors import (
    AssetNotFound,
    InventoryAuthError,
    InventoryError,
    InventoryUnavailable,
    SettingsError,
)
from asset_lookup.models import Asset
from asset_lookup.settings import load_settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="asset-lookup", description="Look up assets in the Orbital Logistics inventory."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    show = commands.add_parser("show", help="show one asset")
    show.add_argument("asset_id")
    listing = commands.add_parser("list", help="list assets")
    listing.add_argument("--team")
    note = commands.add_parser("note", help="add a note to an asset")
    note.add_argument("asset_id")
    note.add_argument("text")
    note.add_argument("--ticket", dest="ticket_id")
    return parser


def format_asset(asset: Asset) -> str:
    return f"{asset.id:<14} {asset.team:<11} {asset.criticality:<7} {asset.name}"


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)  # exits with code 2 on a usage error
    try:
        settings = load_settings()
    except SettingsError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    try:
        with InventoryClient.from_settings(settings) as client:
            if args.command == "show":
                print(format_asset(client.get_asset(args.asset_id)))
            elif args.command == "list":
                for asset in client.list_assets(team=args.team):
                    print(format_asset(asset))
            else:
                note_id = client.add_note(args.asset_id, text=args.text, ticket_id=args.ticket_id)
                print(f"note {note_id} added to {args.asset_id}")
    except (InventoryUnavailable, InventoryAuthError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 3
    except AssetNotFound as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except InventoryError as error:
        print(f"error: unexpected answer from the inventory: {error}", file=sys.stderr)
        return 1
    return 0
