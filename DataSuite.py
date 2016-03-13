from datetime import datetime, timedelta, date
import pytz


def createEntry(pts, reb, ast, stl, blk, tov, tpt, mins):
    """
    Take in stat data & player ID
    Pts/Ast/Reb/Stl/Blk/Tov/3pt
    Return dict of stats, ready for entry
    """

    entry = {"pts": float(pts), "reb": float(reb), "ast": float(ast),
             "stl": float(stl), "blk": float(blk), "tov": float(tov),
             "3pt": tpt, "min": float(mins)}

    return entry


def addEntryToProjectionDict(projection_dict, player_id, entry_dict):
    """
    Takes in dict of stats
    Adds dict entry to projection_dict
    Example: projection_dict = {}
    """
    projection_dict[player_id] = entry_dict


def addProjectionDictForSource(source, template, projection_dict):
    """
    source: number_fire, roto_wire, etc.
    projection_dict: final after all entries added
    Includes timestamp data and count
    """

    # get current time in pst
    now = datetime.now(
          pytz.timezone('US/Pacific')).strftime('%Y-%m-%d %H:%M:%S')

    # add info for source to
    template[source]["scrape_timestamp_pst"] = now
    template[source]["record_count"] = len(projection_dict)
    template[source]["projections"] = projection_dict


def getCurrentDate():
    """
    For final json
    YYYY-MM-DD format
    """
    # current date in pst
    current_date = datetime.now(
                   pytz.timezone('US/Pacific')).strftime('%Y-%m-%d')

    return current_date


def getYesterdayDate():
    """
    For actual NBA stats scraper
    YYYY-MM-DD format
    """
    # yesterday in pst
    yest = (datetime.now(pytz.timezone('US/Pacific')) -
            timedelta(days=1)).strftime('%Y-%m-%d')

    return yest


def getAllGameDates():
    """
    Gets all dates from beginning of season
    Returns array of dates
    """
    start = date(2015, 11, 2)
    end = date(2015, 11, 11)

    delta = timedelta(days=1)

    date_array = []

    while start <= end:
        date_array.append(start.strftime("%Y-%m-%d"))
        start += delta

    return date_array

# print(getAllGameDates())
