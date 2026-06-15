# RCVElectionSystem

A voting website built for elections in an online gaming community (the nation
of Finland on EarthMC, a Minecraft geopolitics server). It implements
[instant-runoff voting](https://en.wikipedia.org/wiki/Instant-runoff_voting):
voters rank candidates, and candidates are eliminated in rounds with their
votes redistributed until a winner emerges.

## Architecture

- Frontend (HTML/CSS/JavaScript): [Jevk](https://github.com/jevk)
- Backend (Python/Flask, served with Waitress): [Emerald](https://github.com/emeraldtip)
- Election configuration via `settings.json` (candidates, opening/closing times
  as Unix timestamps)

## Running it

1. Install the requirements: [Flask](https://github.com/pallets/flask) and
   [Waitress](https://github.com/Pylons/waitress)
2. Add candidate names and opening/closing times to `settings.json`
   (see the example file)
3. For local testing run `application.py`; for deployment run
   `waitress_server.py`, or use `cli.py` and the `start` command

## Known limitations

The first version was built in about 2.5 days for a live election deadline.
Things I would improve for production use:

- HTTPS support (currently HTTP only)
- Input validation and automated tests
- Running on port 80 on Linux requires elevated permissions

Bug reports: [open an issue](https://github.com/jevk/RCVElectionSystem/issues)
