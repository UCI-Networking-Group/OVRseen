#!/usr/bin/python

# This file is a part of OVRseen <https://athinagroup.eng.uci.edu/projects/ovrseen/>.
# Copyright (c) 2021 UCI Networking Group.
#
# This file incorporates content from NoMoATS <http://athinagroup.eng.uci.edu/projects/nomoads/>.
# Copyright (C) 2019 Anastasia Shuba.
#
# OVRseen is dual licensed under the MIT License and the GNU General Public
# License version 3 (GPLv3). This file is covered by the GPLv3. If this file
# get used, GPLv3 applies to all of OVRseen.
#
# See the LICENSE.md file along with OVRseen for more details.

import hashlib, copy, re
import json_keys
from urllib.parse import unquote


class PIIHelper(object):
    """
    Helper class for finding and redacting PII in JSON data, NoMoAds format
    """

    PII_KEY_LOCATION = "Location"
    REDACT_PREFIX = "REDACTED_"
    REDACT_LOCATION = REDACT_PREFIX + PII_KEY_LOCATION.upper()


    def __init__(self, pii_dict, location_coords, should_redact=False):
        """
        :param pii_dict: dictionary containing pii type and its value.
            Both type and value must be of type string. Example:
            {
                "Device ID": "1234",
                "IMEI": "0987"
            }
        :param location_coords: a list of tuples of (latitude, longitude) coordinates. Example:
            [("33.64", "-117.84"), ("33.6", "-117.8")]
        """
        self.pii_redact_values = {}
        self.pii_dict = {}
        self.location_coords = location_coords
        self.should_redact = should_redact

        for pii_key in pii_dict:
            # Add md5 and sha1 hashes to values to search for
            pii_value = pii_dict[pii_key]
            pii_value_encoded = pii_value.encode("utf-8")
            self.pii_dict[pii_key] = [pii_value,
                                      hashlib.md5(pii_value_encoded).hexdigest(),
                                      hashlib.sha1(pii_value_encoded).hexdigest()]

            # Create a redacted version of the pii
            self.pii_redact_values[pii_key] = PIIHelper.REDACT_PREFIX + \
                                              pii_key.upper().replace(" ", "_")


    def _is_numeric(self, value):
        return isinstance(value, int) or isinstance(value, float)


    # returns None if cannot convert
    # if the compared value is some type, then try to make value into that type
    def _get_numberic_value(self, value, compared_value):
        if isinstance(compared_value, int):
            try:
                new_val = int(value)
                return new_val
            except:
                pass
        if isinstance(compared_value, float):
            try:
                new_val = float(value)
                return new_val
            except:
                pass


    def _contains_pii(self, value, pii_key, override_redacting=False):
        """
        Finds the pii that may be inside "value".
        :param value: string that we search for pii
        :param pii_key: pii (key in the self.pii_dict) to search for
        :return: a tuple - (boolean indicating whether the provided pii was found,
                            the provided value with any PII redacted)
        """
        updated_value = value
        pii_found = False

        for pii_value in self.pii_dict[pii_key]:
            match = False
            if self._is_numeric(updated_value):
                numeric_pii_value = self._get_numberic_value(pii_value, updated_value)
                if numeric_pii_value is not None:
                    match = numeric_pii_value == updated_value
            else:
                #match = pii_value.lower() in updated_value.lower()
                match = re.search(pii_value, updated_value, re.I)

            if match:
                pii_found = True
                if self.should_redact and not override_redacting:
                    redact_value = self.pii_redact_values[pii_key]
                    #updated_value = updated_value.replace(pii_value, redact_value)
                    # use case insenstive redacting
                    updated_value = re.sub(pii_value, redact_value, updated_value, flags=re.I)

        return updated_value, pii_found


    def _contains_location_pii_type(self, value):
        """
        Finds and redacts location coordinates that may be inside "value".
        :param value: string that we search for pii
        :return: a tuple - (boolean indicating whether location was found,
                            the provided value with any PII redacted)
        """
        # to compare both lat and longitude, the value needs to be a string
        pii_found = False
        if self._is_numeric(value):
            return value, pii_found

        updated_value = value
        for latitude, longitude in self.location_coords:
            if latitude in updated_value and longitude in updated_value:
                pii_found = True
                if self.should_redact:
                    updated_value = updated_value.replace(latitude, PIIHelper.REDACT_LOCATION)
                    updated_value = updated_value.replace(longitude, PIIHelper.REDACT_LOCATION)

        return updated_value, pii_found


    def get_pii_from_str(self, value, override_redacting=False, url_decoding=True):
        """
        Finds PII in the provided value (must be of string type)
        :return: a tuple - (the provided value with any PII redacted, the list of found PII types)
        """

        new_value = value

        # do nothing for this case
        if value is None:
            return value, []

        # may need to convert unicode (python2)
        #if isinstance(value, unicode):
        #    new_value = value.encode("utf-8")

        # may need to decode
        if url_decoding and re.search(r'%[0-9a-f]', new_value):
            try:
                #print("trying to decode string %s", new_value)
                new_value = unquote(new_value)
                #print("new string after decoding %s", new_value)
            except Exception as e:
                print(str(e))
                pass

        pii_keys_found = []
        updated_value = new_value
        # redact from longer to shorter PII values
        for pii_key, _ in sorted(self.pii_dict.items(), key=lambda t: -len(t[1][0])):
            # find regular pii
            updated_value, pii_found = self._contains_pii(updated_value, pii_key, override_redacting=override_redacting)
            if pii_found:
                pii_keys_found.append(pii_key)

        updated_value, location_found = self._contains_location_pii_type(updated_value)
        if location_found:
            pii_keys_found.append(PIIHelper.PII_KEY_LOCATION)

        return updated_value, pii_keys_found


    def get_pii_from_data(self, json_data):
        """
        Finds PII in the provided JSON data (NoMoAds format expected).
        Currently this method searches for PII in the URI and all HTTP header values
        :return: a tuple - (the provided data with any PII redacted, the list of found PII types)
        """
        redacted_data = copy.deepcopy(json_data) #  make sure we don't modify the original data
        redacted_uri = ""
        pii_keys_found = []
        if json_keys.uri in json_data:
            # don't url_decoding just in case we mess up the path
            redacted_uri, uri_pii_keys_found = self.get_pii_from_str(json_data[json_keys.uri], url_decoding=False)
            pii_keys_found += uri_pii_keys_found

        redacted_data[json_keys.uri] = redacted_uri

        for header_key in json_data[json_keys.headers]:
            # look for PII by header_key, never redact
            _, header_key_pii_keys_found = self.get_pii_from_str(header_key, override_redacting=True)
            pii_keys_found += header_key_pii_keys_found

            # look for PII in header values
            redacted_header, header_pii_keys_found = self.get_pii_from_str(
                                                        json_data[json_keys.headers][header_key])
            redacted_data[json_keys.headers][header_key] = redacted_header
            pii_keys_found += header_pii_keys_found

        return redacted_data, list(set(pii_keys_found))
