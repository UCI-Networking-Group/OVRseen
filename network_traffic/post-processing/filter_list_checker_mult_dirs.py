import os
from adblockparser import AdblockRules
import argparse
import json
import re
import glob
from urllib.parse import urlsplit

from utils import utils

key_referer = "referer"
key_req_with = "x-requested-with"
key_xml_http_req = "xmlhttprequest"

key_http = "http"
key_https = "https"

type_other = 'other'
type_script = 'script'
type_stylesheet = 'stylesheet'
type_image = 'image'
type_subdocument = 'subdocument'

# Patterns for matching URL to find content type (based on AdblockPlus for Android)
# Note: match these against the URL path only, without including URL query and fragment
re_js = re.compile("\.js$", re.IGNORECASE)
re_css = re.compile("\.css$", re.IGNORECASE)
re_image = re.compile("\.(?:gif|png|jpe?g|bmp|ico)$", re.IGNORECASE)
re_html = re.compile("\.html?$", re.IGNORECASE)

# The Android code also includes fonts, but based on https://adblockplus.org/en/filters#options
# this is not a valid option in current ABP
# re_font = re.compile("\.(?:ttf|woff)$", re.IGNORECASE)
def init_rule_checker(filter_list_file):
    """
    Initializer an AdblockRules instance to correspond to a filter list stored in a given file.
    :param filter_list_file: The path to the filter list file.
    :return: An AdblockRules instance initialized to perform matching against the given filter list.
    """
    print("Reading in filter list: %s" % filter_list_file)
    with open(filter_list_file, "r") as f:
        lines = f.readlines()
        return AdblockRules(lines)


def get_content_type(url_parsed):
    """
    Detects content type for the given URL.
    Based on:
    https://github.com/adblockplus/libadblockplus-android/blob/
        bcb385e81d4ce2ead519b662997e0865b79b4fb0/libadblockplus-android-webview/
        src/org/adblockplus/libadblockplus/android/webview/AdblockWebView.java

    :param url_parsed: The parsed URL, as returned by urlsplit
    :return: Content type as a string object that can be used in AdblockRules options
    """
    url_path = url_parsed.path
    type = type_other
    if re_js.search(url_path):
        type = type_script
    elif re_css.search(url_path):
        type = type_stylesheet
    elif re_image.search(url_path):
        type = type_image
    elif re_html.search(url_path):
        type = type_subdocument

    return type


def get_origin(url_parsed):
    """
    Returns the origin of the provided URL.
    Based on: https://developer.mozilla.org/docs/Glossary/Origin

    :param url_parsed: The parsed URL, as returned by urlsplit
    :return: the origin of the URL
    """

    # Origin is defined by schema, host, and port.
    # Note that the resulting origin is not of valid browsing format, but this is not an issue here.
    return url_parsed.scheme + url_parsed.netloc


def isxmlreq_isthirdparty(url_parsed, httpheaders):
    """
    Parses the HTTP headers to find if the request is an xml request and if it's 3rd party

    :param url_parsed: The parsed URL, as returned by urlsplit
    :param httpheaders: HTTP headers in dictionary format, where each key is the HTTP header key,
        and each value is the HTTP header value
    :return: a tuple containing two booleans: (is_xml_request, is_third_party)
    """
    is_third_party = False
    is_xml_request = False
    for key in httpheaders:
        lower_key = key.lower()
        if lower_key == key_referer:
            if get_origin(urlsplit(httpheaders[key])) != get_origin(url_parsed):
                is_third_party = True
        elif lower_key == key_req_with:
            if httpheaders[key].lower() == key_xml_http_req:
                is_xml_request = True

    return (is_xml_request, is_third_party)


def get_options(url, httpheaders):
    """
    Returns the AbblockPlus options to be set for the provided URL and HTTP headers

    :param url: The full URL including query and fragment
    :param httpheaders: HTTP headers in dictionary format, where each key is the HTTP header key,
        and each value is the HTTP header value
    :return: a dictionary of options that can be passed to rules.should_block
    """

    url_parsed = urlsplit(url)
    content_type = get_content_type(url_parsed)
    (is_xml_request, is_third_party) = isxmlreq_isthirdparty(url_parsed, httpheaders)

    return {content_type: True, 'xmlhttprequest': is_xml_request, 'third-party': is_third_party}


def get_url_and_options(pkt_nomoads_json):
    port = pkt_nomoads_json[utils.json_key_dst_port]

    # Note: usually we only deal with HTTP/S:
    url = ""
    if not pkt_nomoads_json[utils.json_key_host].startswith("http://") and \
            not pkt_nomoads_json[utils.json_key_host].startswith("https://"):
        if port == 443:
            url = "https://"
        else:
            url = "http://"

    url += pkt_nomoads_json[utils.json_key_host] + pkt_nomoads_json.get(utils.json_key_uri, "")
    headers = pkt_nomoads_json.get(utils.json_key_headers, {})
    options = get_options(url, headers)

    return url, options


def get_block_decision(ruleset, pkt_nomoads_json, url, options):
    """
    Given a single packet in NoMoAds JSON format, return if the given filter list blocks that packet.
    :param ruleset: an AdblockRules instance that has been initialized with a given set of rules.
    :param pkt_nomoads_json: A single packet in NoMoAds JSON format.
    :return: True if the ruleset would block the packet, False otherwise.
    """

    # We always return False if there is no "host" in the packet
    if utils.json_key_host not in pkt_nomoads_json:
        return False

    return ruleset.should_block(url, options)


def read_nomoads_json(nomoads_json_file):
    """
    Reads a json file in NoMoAds format into memory.
    :param nomoads_json_file: The full path to the NoMoAds json file.
    :return: The in-memory representation of the json file.
    """
    with open(nomoads_json_file, "r") as jf:
        #decoder = json.JSONDecoder()
        #return decoder.decode(jf.read())
        return json.load(jf)


def read_and_annotate_nomoads_json(ruleset, nomoads_json_file, filter_list_name):
    """
    Opens a JSON file that contains packets in NoMoAds format, and annotates each packet with the given AdblockRules'
    block decision. This is merely a utility function that handles reading the json file into memory on behalf of the
    caller and then internally delegates to annotate_nomoads_json.
    :param ruleset: An AdblockRules instance that determines if each individual packet should be blocked or not.
    :param nomoads_json_file: A JSON file with packets in NoMoAds format.
    :param filter_list_name: The key that will point to the block decision in the annotated json.
    :return: The original JSON, annotated with blocking decision and filter list name.
    """
    with open(nomoads_json_file, "r") as jf:
        decoder = json.JSONDecoder()
        root_obj = decoder.decode(jf.read())
        return annotate_nomoads_json(ruleset, root_obj, filter_list_name)


block_decision_cache = dict()

def annotate_nomoads_json(ruleset, nomoads_json, filter_list_name):
    """
    Given an in-memory representation of a NoMoAds json file, annotates each packet with the given AdblockRules' block
    decision. The filter_list_name parameter defines the key that will point to the block decision.
    :param ruleset: An AdblockRules instance that determines if each individual packet should be blocked or not.
    :param nomoads_json: An in-memory representation of a NoMoAds json file.
    :param filter_list_name: The key that will point to the block decision in the annotated json.
    :return: The original JSON, annotated with block decision.
    """
    if filter_list_name not in block_decision_cache:
        block_decision_cache[filter_list_name] = dict()

    annotated = {}
    for key in nomoads_json:
        pkt = nomoads_json[key]
        if utils.json_key_host in pkt:
            url, options = get_url_and_options(pkt)
            url_options_key = url + json.dumps(options, sort_keys=True)
            if url_options_key in block_decision_cache[filter_list_name]:
                blocked = block_decision_cache[filter_list_name][url_options_key]
                #print("Found in cache: ", url_options_key)
            else:
                blocked = get_block_decision(ruleset, pkt, url, options)
                # add to cache
                url_options_key = url + json.dumps(options, sort_keys=True)
                block_decision_cache[filter_list_name][url_options_key] = blocked
        else:
            blocked = False
            #print("Warning, pkt has no ", utils.json_key_host, ", defaulting to blocked = False\n", str(pkt))

        pkt[filter_list_name] = 1 if blocked else 0
        annotated[key] = pkt

    return annotated


def write_annotated_nomoads_json(data, file_out):
    """
    Write annotated NoMoAds JSON to a file.
    :param data: The annotated NoMoAds JSON.
    :param file_out: The file to output the annotated NoMoAds JSON to.
    """
    with open(file_out, "w") as jf:
        jf.seek(0)
        jf.write(json.dumps(data, sort_keys=True, indent=4))
        jf.truncate()


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description="Match packet data against a given set of filter lists.")
    ap.add_argument('nomoads_dirs', type=utils.readable_dirs,
                    help='Directories containing JSON files in NoMoAds JSON format.')
    ap.add_argument('filter_list_dir', type=utils.readable_dir,
                    help='Path to a directory containing filter lists in EasyList (ABP) format.')
    ap.add_argument('out_dir_name', type=str,
                    help='Name of the inner directory we want to save the file to.')
    args = ap.parse_args()

    # Prepare a filter list matcher for each filter list. List will contain a tuple for each filter list, with the first
    # element being the name and the second element the matcher object.
    fl_matchers = []
    for fl_file in os.listdir(args.filter_list_dir):
        if "DS_Store" in fl_file:
            continue
        fl_path = args.filter_list_dir + "/" + fl_file
        ext_start = fl_file.rfind(".")
        if ext_start < 0:
            print("WARNING: skipping filter list file '" + fl_file +
                  "' as the filename does not contain a file extension.")
            continue
        # Name of filter list becomes filename minus file extension
        fl_name = fl_file[0:ext_start]
        if len(fl_file) > 0:
            try:
                fl_matchers.append((fl_name, init_rule_checker(fl_path)))
            except Exception as e:
                print("Could not parse rule file: %s" % fl_path)
                print(e)

    # Now match each input json file against each filter list
    for valid_dir in args.nomoads_dirs:
        print("Processing: ", valid_dir)
        for nomoads_file in glob.iglob(valid_dir + os.sep + "*-nomoads.json"):
            print("Found nomoads json ", nomoads_file)
            nomoads_path = nomoads_file
            if nomoads_file == ".DS_Store":
                continue
            if os.path.isdir(nomoads_path):
                # Skip sub dirs.
                continue
            # Load json file into memory.
            nomoads_json = read_nomoads_json(nomoads_path)
            # Perform rule matching for all filter lists.
            for fl_tup in fl_matchers:
                nomoads_json = annotate_nomoads_json(fl_tup[1], nomoads_json, fl_tup[0])

            # make the output directory
            fl_result_dir = os.path.join(valid_dir, args.out_dir_name)
            if not os.path.isdir(fl_result_dir):
                os.makedirs(fl_result_dir)
            #print("Writing to ", fl_result_dir)
            # Json has now been annotated with blocking decisions for all filter lists. Write result to output dir.
            write_annotated_nomoads_json(nomoads_json, fl_result_dir + os.sep + os.path.basename(nomoads_path))
