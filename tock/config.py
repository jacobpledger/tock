import argparse
from configparser import ConfigParser
import os


class InvalidTockConfigException(Exception):
    pass


class TockConfig(ConfigParser):

    config_filename = os.environ.get("TOCK_CONFIG", "./config.ini")

    def __init__(self):
        super().__init__(allow_no_value=True)
        self.required_arguments = ["Token", "Email", "SubscriptionId"]
        self.read(self.config_filename)
        if not self.has_section("USER"):
            self.add_section("USER")
        if not self.has_section("CACHE"):
            self.add_section("CACHE")

    def set_user_configs(self, args: argparse.Namespace) -> None:

        # Weekends
        if args.include_weekends:
            self.set(
                section="USER",
                option="IncludeWeekends",
                value=str(args.include_weekends),
            )

        # Holidays
        if args.holiday_project_name:
            self.set(
                section="USER",
                option="HolidayProjectName",
                value=args.holiday_project_name,
            )
        if args.holiday_task_name:
            self.set(
                section="USER", option="HolidayTaskName", value=args.holiday_task_name
            )
        if args.country:
            self.set(section="USER", option="Country", value=args.country)
        if args.state:
            self.set(section="USER", option="State", value=args.state)
        if args.province:
            self.set(section="USER", option="Province", value=args.province)

        # Required
        if args.subscription_id:
            self.set(
                section="USER", option="SubscriptionId", value=str(args.subscription_id)
            )
        if args.token:
            self.set(section="USER", option="Token", value=args.token)
        if args.email:
            self.set(section="USER", option="Email", value=args.email)

    def export(self):
        with open(self.config_filename, "w") as f:
            self.write(f)

    def is_valid(self):
        is_valid = True
        try:
            self.validate()
        except InvalidTockConfigException:
            is_valid = False
        return is_valid

    def validate(self):
        missing_arguments = []
        for argument in self.required_arguments:
            if not self.get(section="USER", option=argument, fallback=None):
                missing_arguments.append(argument)
        if any(missing_arguments):
            raise InvalidTockConfigException(
                f"Missing the following required info: {missing_arguments}"
            )
