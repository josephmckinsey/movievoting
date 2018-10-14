# Movie Voting System

My favorite way to decide between movies in large groups.

## Can't decide between Thor: Ragnarok vs. The Net vs. Hackers?
Now you can all enter your rankings for each movie, then this program will spit
out a full ranking in a nice formatted table. Negative numbers should indicate a
desire to watch. Can and do use decimal numbers.

## How does it work?
For each person, you can assign a weighting (typically 1.0 for present, or -1.0
for gone). That way you save movies that everyone wants to watch for when
everyone is available. Then it sorts the list by these rankings.

You only have to do it once for the movies, then you can just delete rows.

### Set Up
1. Set up your movie spreadsheet called "Movies" with tab sheet named "Movies"
   as well. Format it like this
   [template](https://docs.google.com/spreadsheets/d/1BLlKyh5_DDLP9sCiilG4CxOMQ9bTI5YawXqXqIQhf5s/edit?usp=sharing).
   Make sure the columns are correct, or you could change some parameters if you
   want.

2. Download program. Note that it requires ``numpy`, `gspread`, `google_auth`,
   and `terminaltables`.

3. Get a `client_secret.json` to folder for api access. This requires generating
   some OAuth 2.0 credentials and setting up some application information for
   Google's consent screen.

3. Run it. It should direct you to allow access into your google sheets.


## Why the crazy ranking system?
[Arrow's impossibility
theorem](https://en.wikipedia.org/wiki/Arrow's_impossibility_theorem) guarantees
that any ordinal voting system, a voting system that combined integer orderings
into a full orderings, will have some fatal flaw in its construction. However,
the same does not apply to cardinal (real number) voting systems like this one.
By allowing the use of floating points, and essentially ignoring ties, you can
avoid all the annoying properties of most voting systems.

It also works great for unexpected events, since you can just pick something
from the top 5 or something that fits weird criteria.

## But can't you just decide on a movie?
No. The number of movies just got larger and larger. Also, the ability to decide
days in advance gives me enough time to get it from the library.

## Why not use the MATRIX_MULT command in VBA scripting in the spreadsheet?
I don't like VBA. So I needlessly complicated the entire process into this mess:
4 python libraries and an api-key for OAuth 2.0 authentication.

## Why a command line interface?
So it's not tied directly to google sheets. I could switch to just .csv pretty
easily. Plus, it's a lot nicer to look at than google sheets.
