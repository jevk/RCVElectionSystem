# Finnish elections voting site for EarthMC
This is a voting website for the nation of Finland on EarthMC. It employs the [Instant-runoff voting](https://en.wikipedia.org/wiki/Instant-runoff_voting) system, which is a ranked-choice voting system, which eliminates candidates in rounds and distributes their votes to the other candidates, for calculating the results of the election.

The site is not currently live at [vote.cumzon.ee](http://vote.cumzon.ee), but will return someday.

## Requirements
- [Flask](https://github.com/pallets/flask)
- [Waitress](https://github.com/Pylons/waitress)

## Usage
1. Install the required libraries
2. Add candidate names to candidates.txt, each on a separate line
3. Set the opening and closing times in application.py on lines 12 and 13 respectively. The timestamps are in Unix time (seconds since the epoch). [Here's](https://www.unixtimestamp.com/) a useful tool for generating these timestamps
4. If running/testing locally run application.py, otherwise run waitress_server.py

## Disclaimers
- Currently only supports HTTP, HTTPS support is planned in the future
- The code is written in a hurry in about 2.5 days and may have a lot of bugs. If problems occur, please open an issue [here](https://github.com/SpartanJ/ecode/issues)
- Most likely won't run on Linux on port 80 without sudo perms

## Credits:
Frontend by [Jevk](https://github.com/jevk)

Backend by [Emerald](https://github.com/emeraldtip)
