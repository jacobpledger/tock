import argparse
from configparser import ConfigParser
import os


class InvalidTockConfigException(Exception):
    pass


class MissingTockConfigException(Exception):
    pass


class TockConfig(ConfigParser):

    default_section = "DEFAULT"
    user_section = "USER"
    cache_section = "CACHE"

    config_path = os.environ.get(
        "TOCK_CONFIG",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini"),
    )

    def __init__(self):
        super().__init__(allow_no_value=True)
        self.required_arguments = ["Token", "Email", "SubscriptionId"]

        if not os.path.isfile(self.config_path):
            raise MissingTockConfigException("Cannot read configuration file!")

        self.read(self.config_path)
        if not self.has_section(self.user_section):
            self.add_section(self.user_section)
        if not self.has_section(self.cache_section):
            self.add_section(self.cache_section)

    def set_user_configs(self, args: argparse.Namespace) -> None:

        # Weekends
        if args.include_weekends:
            self.set(
                section=self.user_section,
                option="IncludeWeekends",
                value=str(args.include_weekends),
            )

        # Holidays
        if args.holiday_project_name:
            self.set(
                section=self.user_section,
                option="HolidayProjectName",
                value=args.holiday_project_name,
            )
        if args.holiday_task_name:
            self.set(
                section=self.user_section,
                option="HolidayTaskName",
                value=args.holiday_task_name,
            )
        if args.country:
            self.set(section=self.user_section, option="Country", value=args.country)
        if args.state:
            self.set(section=self.user_section, option="State", value=args.state)
        if args.province:
            self.set(section=self.user_section, option="Province", value=args.province)

        # Required
        if args.subscription_id:
            self.set(
                section=self.user_section,
                option="SubscriptionId",
                value=str(args.subscription_id),
            )
        if args.token:
            self.set(section=self.user_section, option="Token", value=args.token)
        if args.email:
            self.set(section=self.user_section, option="Email", value=args.email)

    def export(self):
        with open(self.config_path, "w") as f:
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
            if not self.get(section=self.user_section, option=argument, fallback=None):
                missing_arguments.append(argument)
        if any(missing_arguments):
            raise InvalidTockConfigException(
                f"Missing the following required info: {missing_arguments}"
            )
