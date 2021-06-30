# tock
A Tickspot client.


## Installation

You can (if you want) install this repo using pip. It is not (yet?) in PyPI.

## Use

You can simply run this with `python -m tock` after cloning and entering the project directory.

There are some initial setup parameters that are required, but will be cached in `config.ini` and are therefore only required **once on first run**.
These are: `token`, `email`, and `subscription_id` for authentication, as well as `country` and `province` or `state` for holiday detection.

Additionally, each run requires you to specify a `project`, `task` and `start_date` for the entries.
An entry will be created for that project/task for each day from the start date up to and including today.
If you wish to limit the date range, specify an `end_date` as well. Statutory holidays for your region will be skipped automatically.

Your `token` and `subscription_id` can be found in your Tickspot account profile.

For multi-word projects/tasks, or if they contain special characters, you will have to add quotes around them.
ex. `--task "Doing Stuff"` or `--project "#bigdata"`

Date format *should* be **somewhat** flexible, but I haven't tested anything but yyyy-mm-dd, so I'm sorry if your preferred ~~wrong~~ format doesn't work right.

By default, each entry is for 8 hours, but this can be overridden by specifying `hours`, and **that value will be cached for subsequent runs**.

Also by default, weekends will be skipped. You can override this by adding the `--include_weekends` flag.
