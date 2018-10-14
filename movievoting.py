"""Movie Voting System: Optimize your movie choices"""

import inspect
from textwrap import wrap

import gspread
import numpy
import terminaltables
from google_auth_oauthlib.flow import Flow


class Credentials:
    "This is a complete hack to work with gspread and google-auth."
    def __init__(self, token, refresh):
        self.access_token = token
        self.refresh = refresh

    def debug_print(self):
        "Aid in debugging this mess"
        print("------ Access Token --------")
        print(self.access_token)
        print("------ Refresh --------")
        print(inspect.getsource(self.refresh))

    @classmethod
    def from_flowcred(cls, flow_cred):
        """Create flowcred using deprecated flowcred object"""
        return cls(flow_cred.token, flow_cred.refresh)


def get_credentials():
    """Generates new credentials for google api.

    TODO: google_auth has yet to implement storage, so that may have wait for
    another day.
    TODO: This also doesn't automatically open in your browser.

    """
    # We only need read permissions.
    scopes = ['https://www.googleapis.com/auth/drive.readonly',
              'https://www.googleapis.com/auth/spreadsheets.readonly']

    flow = Flow.from_client_secrets_file(
        'client_secret.json', scopes,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob')

    auth_url, _ = flow.authorization_url(prompt='consent')
    print('Go to')
    print(auth_url)
    print('and copy Auth Code')

    code = input('Enter auth code: ')
    print("Fetching Token.")
    flow.fetch_token(code=code)
    return flow.credentials

def get_column(wks, row, col, number):
    """Get column with starting row and column, and then going down `number`
rows."""
    return list(map(lambda x: x.value,
                    wks.range(row, col, number+row-1, col)))

class Movie:
    """Define a movie class. Should probably be replaced with dictionary."""
    def __init__(self, name, streaming, notes, veto):
        self.name = name
        self.streaming = streaming
        self.notes = notes
        self.veto = veto

class Movies:
    """Handles movie information as well as weighted rankings"""
    def __init__(self, movies, people, rankings):
        """Define all the things!"""
        self.movies = movies
        self.people = people
        self.rankings = rankings
        self.votes = []
        self.weighted_ranking = rankings
        self.sorting = rankings



    @classmethod
    def from_worksheet(cls, wks):
        """Grab all the necessary information if it is laid out as expected. See
template for actual understanding behind this."""
        print("Getting movie information based on template")
        # See the movie spreadsheet for values it is creating. The +2 terms came from
        # mostly trial and error.
        row_start = 3

        movie_names = wks.col_values(1)[2:]
        num_movies = len(movie_names)

        streaming = get_column(wks, row_start, 2, num_movies)
        notes = get_column(wks, row_start, 3, num_movies)
        veto = get_column(wks, row_start, 4, num_movies)

        movies = []
        for i in range(num_movies):
            movies.append(
                Movie(movie_names[i], streaming[i],
                      notes[i], veto[i])
            )

        # This should allow for any number of people voting
        num_col = len(wks.row_values(2))
        people = list(map(lambda x: x.value, wks.range(2, 5, 2, num_col)))

        print("Getting people's scores")
        # Gets the whole matrix of values
        unprocessed_rankings = wks.range(3, 5, num_movies+2, num_col)

        # Move out of cells. Convert to float. And turn it into a matrix.
        rankings = numpy.reshape(list(map(lambda x: float(x.value),
                                          unprocessed_rankings)),
                                 (num_movies, num_col - 5 + 1))

        return cls(movies, people, rankings)

    def input_votes(self):
        """Reset inputs from user input"""
        # Request the votings. Use positives for people who are here, and negatives for
        # people who aren't.
        print("\nPlace equal positive values for people present\
and negative for those absent.")
        self.votes.clear()
        for i in self.people:
            self.votes.append(float(input(str(i) + ': ')))

    def calculate_weights(self):
        """Use matrix multiplication to apply weights to rankings. Stores sorted
values to self.sorting."""
        self.weighted_ranking = self.rankings.dot(self.votes)
        self.sorting = list(reversed(self.weighted_ranking.argsort()))

    def pretty_table(self):
        """Formats nice table with `terminaltables` package. Returns unicode string
that you can then print."""
        data = []
        for i in self.sorting:
            entry = self.movies[i]
            data.append([entry.name, entry.streaming, '',  # notes is blank for wrapping
                         entry.veto, self.weighted_ranking[i]])

        # Should use fancy terminal characters for seamless lines.
        table = terminaltables.SingleTable(data)
        table.inner_heading_row_border = False  # We don't take about titles.

        # We need the max width available for notes, so we can wrap it correctly.
        max_width = table.column_max_width(2)  # 2 is the index for notes field.

        # We want to wrap all of the notes fields (see textwrap). Then we use it to
        # replace the table_data.
        for i, sorted_i in enumerate(self.sorting):
            wrapped_notes = '\n'.join(
                wrap(self.movies[sorted_i].notes, max_width)
            )
            table.table_data[i][2] = wrapped_notes
        return table.table  # need to return the string


print("Authorizing spreadsheet access.")
credentials = Credentials.from_flowcred(get_credentials())
gc = gspread.authorize(credentials)


# Open a worksheet from spreadsheet with one shot
print('Opening "Movies" spreadsheet and "Movies" sheet')
worksheet = gc.open("Movies").worksheet('Movies')

what_to_watch = Movies.from_worksheet(worksheet)
what_to_watch.input_votes()
what_to_watch.calculate_weights()
print()
print(what_to_watch.pretty_table())
