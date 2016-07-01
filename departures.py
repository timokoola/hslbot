# -*- coding: utf-8 -*-
from datetime import datetime
from collections import defaultdict

from requests import get, exceptions
from pytz import timezone
import boto3


class HslUrls(object):
    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.baseurl = "http://api.reittiopas.fi/hsl/prod/?request="

    def nearby_stops(self, longitude, latitude):
        url = "%sstops_area&epsg_in=4326&" \
              "center_coordinate=%s,%s&user=%s&pass=%s" % \
              (self.baseurl, latitude, longitude, self.user, self.password)
        return url

    def stop_info(self, stop_code):
        url = "%sstop&epsg_out=4326&code=%s&user=%s&pass=%s" % (
            self.baseurl, stop_code, self.user, self.password)
        return url

    def lines_info(self, lines):
        lines_str = "|".join(lines)
        url = "%slines&epsg_out=4326&query=%s&user=%s&pass=%s" % (
            self.baseurl, lines_str, self.user, self.password)
        return url


def hsl_time_to_time(hsltime):
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
    return "in %d minutes" % (stoptimeagg - nowagg)


class HslRequests(object):
    def __init__(self, user, password):
        self.urls = HslUrls(user, password)
        self.last_error = None

    def stop_summary(self, stop_code):
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
                 in stop["departures"][:3]])
        else:
            departure_line = ""

        return "\n".join([stop_line, departure_line])

    def relative_time(self, stop_code):
        (stop_info, l) = self._stop_info_lines_info(stop_code)
        s = stop_info[0]
        if l:
            lines = dict([(x["code"], "%s %s" % (
                vehicle_map(x["transport_type_id"]), x["code_short"])) for x in
                          l])
            summary_lines = dict(
                [(x["code"], "%s %s" % (x["code_short"], x["line_end"])) for x
                 in l])
        else:
            return ("Helsinki area has no such stop.",
                    "Helsinki area has no such stop.",
                    None)

        actual_code = s["code_short"]
        stop_line = u"For stop {0:s}".format(actual_code)

        if s["departures"]:
            departure_line = (
                ["%s %s" % (lines[x["code"]], relative_minutes(x["time"])) for x
                 in
                 s["departures"][:3]])
            summary_line = "\n".join(
                ["%s %s" % (
                    hsl_time_to_time(x["time"]), summary_lines[x["code"]]) for x
                 in
                 s["departures"][:3]])
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
        card = "\n".join([stop_line, summary_line])

        return (speech, card, actual_code)

    def _stop_info_lines_info(self, stop_code):
        try:
            stop_info = self._stop_info_json(stop_code)
        except:
            stop_info = "Error"
        if stop_info == "Error":
            return "Error", None
        lines_info = self._lines_info(self._stop_buses(stop_info))
        return (stop_info, lines_info)

    def _stop_info_json(self, stop_code):
        url = self.urls.stop_info(stop_code)
        try:
            r = get(url)
        except exceptions.RequestException:
            return "Error"
        return r.json()

    def _stop_buses(self, json):
        l = json[0]["lines"]
        return [x.split(":")[0] for x in l]

    def _lines_info(self, lines):
        url = self.urls.lines_info(lines)
        try:
            r = get(url)
        except exceptions.RequestException:
            return "Error"
        return r.json()

    def stop_lines_summary(self, stop_code):
        """Return bus code, name, address, and lines going from this stop"""
        (stop_info, l) = self._stop_info_lines_info(stop_code)
        s = stop_info[0]

        if l:
            linecodes = dict([(x["code"], x["code_short"]) for x in l])
        else:
            return "Helsinki area has no such bus stop" % stop_code

        d = dict(map(lambda x: x.split(":"), s["lines"]))

        stop_line = s["code_short"] + " " + s["name_fi"] + " " + s["address_fi"]
        ends_lines = [(d[k].split(",")[0], linecodes[k]) for k in d.keys()]

        d = defaultdict(list)

        for last, code in ends_lines:
            d[last].append(code)

        sumsum = ", ".join(
            ["%s %s" % (", ".join(sorted(d[k])), k) for k in sorted(d.keys())])

        return "\n".join([stop_line, sumsum])

    def _location_stops(self, longitude, latitude):
        url = self.urls.nearby_stops(longitude, latitude)
        try:
            r = get(url)
        except exceptions.RequestException:
            return "Error"
        return r.json()

    def stops_for_location(self, longitude, latitude):
        s = self._location_stops(longitude, latitude)

        if s == "Error":
            return "No stops nearby this location"

        return "\n".join(
            ["%s %s %s" % (x["codeShort"], x["name"], x["address"]) for x in s])
