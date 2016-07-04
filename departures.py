"""Classes and functions for accessing Helsinki area traffic data for more info
 see http://developer.reittiopas.fi/pages/en/http-get-interface.php"""
# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime
from pytz import timezone
from requests import get, exceptions


class HslUrls(object):
    """Helper class for building up HSL urls"""

    def __init__(self, user, password):
        """
        Initializer
        :param user: username registered for HSL API
        :param password: associated password
        """
        self.user = user
        self.password = password
        self.baseurl = "http://api.reittiopas.fi/hsl/prod/?request="

    def nearby_stops(self, longitude, latitude):
        """Get an URL to request nearby bus stops
        :param longitude: longitude of the location
        :param latitude: latitude of the location
        :return: URL
        """
        url = "%sstops_area&epsg_in=4326&" \
              "center_coordinate=%s,%s&user=%s&pass=%s" % \
              (self.baseurl, latitude, longitude, self.user, self.password)
        return url

    def stop_info(self, stop_code):
        """
        Get an URL to fetch information about a bus stop
        :param stop_code: code of the stop
        :return: URL
        """
        url = "%sstop&epsg_out=4326&code=%s&user=%s&pass=%s" % (
            self.baseurl, stop_code, self.user, self.password)
        return url

    def lines_info(self, lines):
        """
        Builds up URL to query line info
        :param lines: array of stop codes
        :return: URL
        """
        lines_str = "|".join(lines)
        url = "%slines&epsg_out=4326&query=%s&user=%s&pass=%s" % (
            self.baseurl, lines_str, self.user, self.password)
        return url

    def geocode_address(self, query):
        """
        Builds up URL to search for stops around a search term
        (API recognizes places, addresses etc.
        api.reittiopas.fi/hsl/prod/?request=geocode&key=
        :param query: search term
        """
        url = "%sgeocode&key=%s&user=%s&pass=%s" % (self.baseurl,
                                                    query, self.user,
                                                    self.password)
        return url


def hsl_time_to_time(hsltime):
    """
    Converts HSL API timestamp to hh:dd format
    :param hsltime: HSL API timestamp (hour maybe bigger than 24!)
    :return: timestamp in hh:dd format
    """
    return "%02d.%02d" % (hsltime / 100 % 24, hsltime % 100)


# 1 = Helsinki internal bus lines
# 2 = trams
# 3 = Espoo internal bus lines
# 4 = Vantaa internal bus lines
# 5 = regional bus lines
# 6 = metro
# 7 = ferry
# 8 = U-lines
# 12 = commuter trains
# 21 = Helsinki service lines
# 22 = Helsinki night buses
# 23 = Espoo service lines
# 24 = Vantaa service lines
# 25 = region night buses
# 36 = Kirkkonummi internal bus lines
# 39 = Kerava internal bus lines
def vehicle_map(veh):
    """Maps a vehicle type id to a name
    :param veh: vehicle type id
    :return: vehicle type name
    """
    if veh == 2:
        return "Tram"
    elif veh == 6:
        return "Metro"
    elif veh == 7:
        return "Ferry"
    elif veh == 12:
        return "Train"
    else:
        return "Bus"


def relative_minutes(stoptime, comparison_time=None):
    """
    Change timestamp of HSL API to relative time
    :param stoptime: API timestamp for a vehicle passing a stop
     (note that hour can be more than 24!)
    :param comparison_time: datetime to compare the departure time to
    if None use current timestamp
    :return:
    """
    if comparison_time:
        usertime = comparison_time
    else:
        usertime = datetime.now(tz=timezone("Europe/Helsinki"))
    sth = stoptime / 100
    if sth >= 24 and usertime.hour < 12:
        nowagg = (usertime.hour + 24) * 60 + usertime.minute
    else:
        nowagg = usertime.hour * 60 + usertime.minute
    stm = stoptime % 100
    stoptimeagg = sth * 60 + stm
    delta = stoptimeagg - nowagg
    if delta == 0:
        return "Right now"
    else:
        return "in %d minutes" % (delta)


class HslRequests(object):
    """Class for making requests to HSL API"""

    def __init__(self, user, password):
        """
        Initializer
        :param user: HSL API username
        :param password: HSL API password
        """
        self.urls = HslUrls(user, password)
        self.last_error = None

    def stop_summary(self, stop_code, buses=3):
        """
        Provides an summary of bus stop information including departures
        :param stop_code: HSL API stop code
        :return: String containing bus and departures info
        """
        (stop_info, line_data) = self._stop_info_lines_info(stop_code)
        stop = stop_info[0]
        if line_data:
            lines = dict(
                [(x["code"], "%s %s" % (x["code_short"], x["line_end"])) for x
                 in line_data])
        else:
            return ("Helsinki area has no such stop.",
                    "Helsinki area has no such stop.")

        stop_line = stop["code_short"] + " " + stop["name_fi"] + " " \
                    + stop["address_fi"]

        if stop["departures"]:
            departure_line = "\n".join(
                ["%s %s" % (hsl_time_to_time(x["time"]), lines[x["code"]]) for x
                 in stop["departures"][:buses]])
        else:
            departure_line = ""

        return "\n".join([stop_line, departure_line])

    def relative_time(self, stop_code, buses=3, end_line=""):
        """
        Provides an summary of bus stop information including departures
        used by the Alexa skill and Telegram bot
        :param buses: how many buses to return
        :param stop_code: HSL API stop code
        :return: String containing bus and departures info
        """
        (stop_info, linfo) = self._stop_info_lines_info(stop_code)
        sinfo = stop_info[0]
        if linfo:
            lines = dict([(x["code"], "%s %s" % (
                vehicle_map(x["transport_type_id"]), x["code_short"])) for x in
                          linfo])
            summary_lines = dict(
                [(x["code"], "%s %s" % (x["code_short"], x["line_end"])) for x
                 in linfo])
        else:
            return ("Helsinki area has no such stop.",
                    "Helsinki area has no such stop.",
                    None)

        actual_code = sinfo["code_short"]
        stop_line = u"For stop {0:s}".format(actual_code)
        card_stop_line = sinfo["name_fi"] + " " \
                         + sinfo["address_fi"]

        if sinfo["departures"]:
            departure_line = (
                ["%s %s" % (lines[x["code"]], relative_minutes(x["time"])) for x
                 in
                 sinfo["departures"][:buses]])
            summary_line = "\n".join(
                ["%s %s" % (
                    hsl_time_to_time(x["time"]), summary_lines[x["code"]]) for x
                 in
                 sinfo["departures"][:buses]])
        else:
            departure_line = ["No departures within next 60 minutes"]
            summary_line = "No departures within next 60 minutes"

        if len(departure_line) == 1:
            speech = "%s: %s" % (stop_line, departure_line[0])
        elif len(departure_line) == 2:
            speech = "%s: Next departures are %s and %s" % (
                stop_line, departure_line[0], departure_line[1])
        elif len(departure_line) == 3:
            speech = "%s: Next departures are %s, %s, and %s" % (
                stop_line, departure_line[0], departure_line[1],
                departure_line[2])
        else:
            speech = "%s: Next departures are %s" % (
                stop_line, ",".join(departure_line))
        card = "\n".join([card_stop_line + end_line, summary_line])

        return (speech, card, actual_code)

    def _stop_info_lines_info(self, stop_code):
        """
        Helper function
        :param stop_code: HSL API bus stop code
        """
        try:
            stop_info = self._stop_info_json(stop_code)
        except:
            stop_info = "Error"
        if stop_info == "Error":
            return "Error", None
        lines_info = self._lines_info(_stop_buses(stop_info))
        return (stop_info, lines_info)

    def _stop_info_json(self, stop_code):
        """
        Helper function
        :param stop_code: HSL API bus stop code
        """
        url = self.urls.stop_info(stop_code)
        try:
            response = get(url)
        except exceptions.RequestException:
            return "Error"
        return response.json()

    def _lines_info(self, lines):
        """
        Helper function to fetch line information of listed lines
        :param lines: list of HSL API line codes
        """
        url = self.urls.lines_info(lines)
        try:
            response = get(url)
        except exceptions.RequestException:
            return "Error"
        return response.json()

    def stop_lines_summary(self, stop_code):
        """Return bus code, name, address, and lines going from this stop
        :param stop_code: HSL API stop code
        :return: comma separated string of stop info
        """
        (stop_info, linfo) = self._stop_info_lines_info(stop_code)
        sinfo = stop_info[0]

        if linfo:
            linecodes = dict([(x["code"], x["code_short"]) for x in linfo])
        else:
            return "Helsinki area has no bus stop " + stop_code

        dld = dict([x.split(":") for x in sinfo["lines"]])

        stop_line = sinfo["code_short"] + " " + sinfo["name_fi"] + " " + sinfo[
            "address_fi"]
        ends_lines = [(dld[k].split(",")[0], linecodes[k]) for k in dld.keys()]

        ddl = defaultdict(list)

        for last, code in ends_lines:
            ddl[last].append(code)

        sumsum = ", ".join(
            ["%s %s" % (", ".join(sorted(ddl[k])), k) for k in
             sorted(ddl.keys())])

        return "\n".join([stop_line, sumsum])

    def _location_stops(self, longitude, latitude):
        """
        Fetch stops at location using HSL API
        :param longitude: longitude of the location
        :param latitude: latitude of the location
        :return: new line separted list of close by stops
        """
        url = self.urls.nearby_stops(longitude, latitude)
        try:
            response = get(url)
        except exceptions.RequestException:
            return "Error"
        return response.json()

    def _search_result_stops(self, query):
        """
        Fetch stops by search term
        :param query:
        :return: JSON returned from HSL API
        """
        url = self.urls.geocode_address(query)
        try:
            response = get(url)
        except exceptions.RequestException:
            return "Error"
        return response.json()

    def stops_for_query(self, query):
        """
        Return
        :param query:
        """
        stops = self._search_result_stops(query)

        if stops == "Error":
            return "No stops nearby this location"

        return ("\n".join(
            ["%s %s %s" % (
                x["details"]["shortCode"], x["name"], x["details"]["address"])
             for x
             in
             stops if x["locType"] == "stop"]),
                ["%s" % x["details"]["shortCode"] for x in stops if
                 x["locType"] == "stop"])

    def stops_for_location(self, longitude, latitude):
        """
        Get stops at location
        :param longitude: longitude of the location
        :param latitude: latitude of the location
        :return: new line separted list of close by stops
        """
        stops = self._location_stops(longitude, latitude)

        if stops == "Error":
            return "No stops nearby this location"

        return ("\n".join(
            ["%s %s %s" % (x["codeShort"], x["name"], x["address"]) for x in
             stops]), ["%s" % x["codeShort"] for x in stops])


def city_code(city):
    """
    :param city: city is a custom slot type in the alexa skill configuration
    possible values are:
    Helsinki
    Helsingfors
    Espoo
    Esbo
    Vantaa
    Vanda
    Kauniainen
    Grankulla
    :return: a short code is in HSL bus stops. "" for Helsinki, "E" for Espoo
    "V" for Vantaa and "Ka" for Kauniainen
    """
    lc_city = city.lower()
    if lc_city == "helsinki" or lc_city == "helsingfors":
        return ""
    elif lc_city == "espoo" or lc_city == "esbo":
        return "E"
    elif lc_city == "vantaa" or lc_city == "vanda":
        return "V"
    elif lc_city == "kauniainen" or lc_city == "grankulla":
        return "Ka"
    else:  # silently default to Helsinki
        return ""


def normalize_stopcode(code):
    """
    Make stopcode a four digit, zero padded string
    :param code: raw cod
    :return: normalized code
    """
    return format(int(code), '04')


def _stop_buses(json):
    """
    Helper function for enumerating buses going through the stop
    :param json: HSL API bus stop code
    """
    lines = json[0]["lines"]
    return [x.split(":")[0] for x in lines]
