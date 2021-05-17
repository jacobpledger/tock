#!/usr/bin/env python3

import argparse
from configparser import ConfigParser
from datetime import datetime

from dateutil.parser import parse
from dateutil.rrule import rrule, DAILY
import holidays

from tock.config import TockConfig
from tock.tick.client import TickClient


def collect_args(config: ConfigParser) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    # Configuration Options
    # ---------------------

    # Token
    parser.add_argument(
        "--token",
        type=str,
        required=False,
        help="Your Tick API token.",
    )

    # Email
    parser.add_argument(
        "--email",
        type=str,
        required=False,
        help="Your Tickpot-registered email address.",
    )

    # Subscription ID
    parser.add_argument(
        "--subscription_id",
        type=int,
        required=False,
        help="Your Tick subscription ID.",
    )

    # Country
    parser.add_argument(
        "--country",
        type=str,
        required=False,
        help="The country whose holidays you observe.",
    )

    # State
    parser.add_argument(
        "--state",
        type=str,
        required=False,
        help="The state whose holidays you observe.",
    )

    # Province
    parser.add_argument(
        "--province",
        type=str,
        required=False,
        help="The province whose holidays you observe.",
    )

    # Include Weekends
    parser.add_argument(
        "--include_weekends",
        action="store_true",
        required=False,
        help="Tells Tock to fill in entries on weekends as well as weekdays.",
    )

    # Stat Holiday Project
    parser.add_argument(
        "--holiday_project_name",
        type=str,
        required=False,
        help="The project name under which statutory holidays are stored, if tracked.",
    )

    # Stat Holiday Task
    parser.add_argument(
        "--holiday_task_name",
        type=str,
        required=False,
        help="The task name under which statutory holidays are stored, if tracked.",
    )

    # Per-run Parameters
    # ------------------

    # Project
    parser.add_argument(
        "-p",
        "--project",
        type=str,
        required=False,
        help="The project you want to add entries to.",
    )

    parser.add_argument(
        "-t",
        "--task",
        type=str,
        required=False,
        help="The task you want to add entries to.",
    )

    # Notes
    parser.add_argument(
        "-n",
        "--notes",
        type=str,
        required=False,
        default="",
        help="Notes on the entries.",
    )

    # Start Date
    parser.add_argument(
        "--start_date",
        type=str,
        required=True,
        help="The date you want to backfill FROM.",
    )

    # End Date
    parser.add_argument(
        "--end_date",
        type=str,
        default=datetime.today(),
        help="The date you want to backfill TO.",
    )

    # Hours
    parser.add_argument(
        "--hours",
        type=float,
        default=float(config.get(section="USER", option="Hours")),
        help="Hours to fill in for each entry.",
    )

    # Interactive
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="If provided, Tock will ask you to confirm each entry.",
    )

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    config = TockConfig()
    args: argparse.Namespace = collect_args(config=config)
    config.set_user_configs(args=args)
    config.validate()

    client = TickClient(
        token=config.get(section="USER", option="Token"),
        subscription_id=int(config.get(section="USER", option="SubscriptionId")),
        email=config.get(section="USER", option="Email"),
    )

    # TODO: if no start date provided, use date after most recent entry
    # Not sure how to do this yet, because start and end date are
    # mandatory.

    # Get ourselves a date range.
    start_date = parse(args.start_date)
    end_date = (
        parse(args.end_date)
        if not isinstance(args.end_date, datetime)
        else args.end_date
    )
    days = list(
        rrule(DAILY, dtstart=start_date).between(start_date, end_date, inc=True)
    )
    if not bool(config.get(section="USER", option="IncludeWeekends")):
        days = [day for day in days if day.isoweekday() < 6]

    # Get which days are holidays.
    local_holidays = getattr(holidays, config.get(section="USER", option="Country"))(
        prov=config.get(section="USER", option="Province", fallback=None),
        state=config.get(section="USER", option="State", fallback=None),
    )

    # Check if we cross a holiday, and log appropriately.
    crosses_holiday = any([day in local_holidays for day in days])

    if crosses_holiday:
        project = client.get_project_by_name(
            name=config.get(section="USER", option="HolidayProjectName")
        )
        task = client.get_project_task_by_name(
            project_id=project["id"],
            name=config.get(section="USER", option="HolidayTaskName"),
        )
        config.set("CACHE", "HolidayTaskId", str(task["id"]))

    project = client.get_project_by_name(name=args.project)
    task = client.get_project_task_by_name(project_id=project["id"], name=args.task)

    config.export()

    for day in days:
        if day in local_holidays:
            entry = {
                "date": day.strftime("%Y-%m-%d"),
                "hours": 8.0,
                "notes": config.get(section="USER", option="HolidayNotes"),
                "task_id": config.get(section="CACHE", option="HolidayTaskId"),
            }
        else:
            entry = {
                "date": day.strftime("%Y-%m-%d"),
                "hours": args.hours,
                "notes": args.notes,
                "task_id": task["id"],
            }

        if args.interactive:
            print(
                f"Will create the following entry:\n{entry}\n\nProceed (y/n)? (C-c to abort)"
            )
            i = input()
            if i == "y":
                response = client.create_entry(entry=entry)
            else:
                continue
        else:
            response = client.create_entry(entry=entry)
        print(response)
        print(response.json())
