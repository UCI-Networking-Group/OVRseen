import unicodecsv as csv
import argparse
import tldextract


class DeviceAppInfo:
    """
    Stores information about an app such as what hostnames it contacted.
    """

    def __init__(self, app_id, app_name, package_name, developer_name, app_package, policy_url):
        self.app_id = app_id
        self.app_name = app_name
        self.package_name = package_name
        self.developer_name = developer_name or ""
        self.app_package = app_package
        self.policy_url = policy_url
        # Set of hostnames this app contacted.
        self.contacted_hostnames = set()

    def is_contacting_hostname(self, hostname):
        return hostname in self.contacted_hostnames

    def set_contacts_hostname(self, hostname):
        self.contacted_hostnames.add(hostname)


def _is_potential_platform(hostname):
    for token in PLATFORM_TOKENS:
        if token.lower() in hostname:
            return True
    return False


def _is_platform(app_info, hostname, consider_domain_only=False):
    # here we are more sure that it is due to platform
    # if the packagename does not match the app_id, then we know it is most likely a platform specific service
    # meaning the platform (oculus) is contacting the hostname or SLD
    if not consider_domain_only:
        if app_info.package_name not in app_info.app_id:
            package_name_tokens = app_info.package_name.split(".")
            for token in package_name_tokens:
                if token.lower() in PLATFORM_TOKENS:
                    return True
    else:
        return _is_potential_platform(hostname)

    return False


def _get_second_level_domain_from_tld(url_tld):
    return url_tld.domain + "." + url_tld.suffix


def _is_first_party(sld, package_name, current_app, host_name):
    # force first party?
    if FORCE_FIRST_PARTY.get(package_name) and (host_name in FORCE_FIRST_PARTY.get(package_name) or sld in FORCE_FIRST_PARTY.get(package_name)):
        print("First party due to forcing - package name %s, hostname %s" %
              ( package_name, host_name))
        return True

    # tokenize package_name
    package_name_tokens = package_name.split(".")
    package_name_tokens = [x.lower() for x in package_name_tokens if x.lower() not in IGNORE_PACKAGE_TOKENS and len(x.strip()) > 2]

    dest_domain_parsed = tldextract.extract(host_name)

    # extract the eSLD for comparison
    # if it's hosted on a cloud service, take the subdomain instead
    if dest_domain_parsed.registered_domain in CLOUD_PROVIDER_DOMAINS:
        domain_cmp = dest_domain_parsed.subdomain
    else:
        domain_cmp = dest_domain_parsed.registered_domain
        assert sld.replace('.', '').isdigit() or sld == (domain_cmp or '.')

    # check privacy policy url first
    if current_app.policy_url and current_app.policy_url != "N/A":
        policy_domain_parsed = tldextract.extract(current_app.policy_url)
        if policy_domain_parsed.registered_domain == domain_cmp:
            print("First party due to privacy url %s, package name %s, hostname %s" %
                  (current_app.policy_url, package_name, host_name))
            return True

    # we double check if developer has FIRST_PARTY_TOKENS in it. If so, then we allow it.
    for developer_key in DEVELOPER_FIRST_PARTY_TOKENS:
        if developer_key in package_name_tokens and developer_key not in current_app.developer_name.lower():
            print("Removing %s from tokens before determining at first party" % developer_key)
            package_name_tokens.remove(developer_key)

    print("SLD %s, Tokens %s" % (domain_cmp, ",".join(package_name_tokens)))

    # check tokens in package name
    for token in package_name_tokens:
        if token in domain_cmp:
            print("Return first party matched package name token with sld: " + domain_cmp)
            return True

    return False


def get_ais_key(app_id, package_name):
    return app_id+package_name


def get_party_labels(sld, current_app, hostname):
    party_labels = []

    package = current_app.app_package
    if not package or len(package) == 0:
        package = current_app.package_name

    # is hostname contacted by multiple apps?
    apps_contacted = hostname_to_apps[sld]
    if apps_contacted and len(apps_contacted) > 1:
        # good chance it could be third party
        same_developer = True
        for other_app in apps_contacted:
            if other_app.developer_name != current_app.developer_name:
                same_developer = False
                break

        if not same_developer:
            if _is_first_party(sld, package, current_app, hostname):
                party_labels.append(FIRST_PARTY)
            else:
                party_labels.append(THIRD_PARTY)
                if _is_platform(current_app, hostname, consider_domain_only=True):
                    party_labels.append(PLATFORM)

            return party_labels

    # if we reach here, we know it is either first_party, unknown, potential platform

    if _is_first_party(sld, package, current_app, hostname):
        party_labels.append(FIRST_PARTY)
    else:
        if _is_platform(current_app, hostname, consider_domain_only=True):
            party_labels.append(PLATFORM)

    if len(party_labels) == 0:
        party_labels.append(UNKNOWN_PARTY)

    return party_labels

# =================== CSV column names ===================
csv_key_app_id = "app_id"
csv_key_hostname = "hostname"
# package name is what antmonitor picked up
csv_key_package_name = "package_name"
# app package is tied to the app name
csv_key_app_package = "app_id"
csv_key_app_name_from_web_store = "App_Title"
csv_key_app_developer_oculus = "oculus_creator"
csv_key_app_developer_sidequest = "sidequest_creator"
csv_key_sld_label = "second_level_domain"
csv_key_policy_url = "Actual_Developer_Privacy_Policy"

# ========================================================

platform_id_oculus = "oculus"

# labels with third-party and unknown merged together
csv_key_party_label = "party_labels"

# real labels with unknown
csv_key_real_party_label = "real_party_labels"

FIRST_PARTY = "first_party"
THIRD_PARTY = "third_party"
UNKNOWN_PARTY = "unknown_party"
PLATFORM = "platform_party"
SYSTEM_APP_TOKENS = ["oculus", "facebook", "android", "qualcomm"]
PLATFORM_TOKENS = ["oculus", "facebook"]

DEVELOPER_FIRST_PARTY_TOKENS = ["oculus", "facebook", "unity"]
IGNORE_PACKAGE_TOKENS = ["com", "android", "free", "paid", "co"]
CLOUD_PROVIDER_DOMAINS = ["amazonaws.com", "digitaloceanspaces.com"]

# special to our dataset
FORCE_FIRST_PARTY = dict()
FORCE_FIRST_PARTY["com.SoaringRocStudio.LetsGoChopping"] = ["soaringrocdev.github.io"]
FORCE_FIRST_PARTY["com.onehamsa.RNXQ"] = ["racketnx-backend-prod-crates.s3-us-west-1.amazonaws.com",
                                          "racketnx-config.s3-us-west-1.amazonaws.com",
                                          "us-west-1-prod-avatar-rnx-storage.s3.amazonaws.com",
                                          ]
FORCE_FIRST_PARTY["com.vertigogames.azsq"] = ["vertigo-games.com"]
FORCE_FIRST_PARTY["com.resolutiongames.baitsantacruz"] = ["resgam.com"]
FORCE_FIRST_PARTY["com.golfscope.proputt"] = ["api.topgolfvr.com"]
FORCE_FIRST_PARTY["com.ivre.engage"] = ["d71b97dri9uky.cloudfront.net"]
FORCE_FIRST_PARTY["com.StudioHORANG.SphereToonQuest"] = ["220.230.112.14"]


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description="Given a csv of pkts/flows for Oculus, we label each one whether it is first party, thirdparty, unknown, potential platform")
    ap.add_argument("in_csv", help="CSV where each row represents an app pkt/flow within " +
                    platform_id_oculus + ".")
    ap.add_argument("out_csv", help="Output CSV where to write results.")

    args = ap.parse_args()

    # Dict mapping an app ID to an AppInfo
    ais = {}

    # Dict mapping of hostname to a list of appinfo
    hostname_to_apps = {}

    hostname_to_sld = {}

    # Read data from CSV and create in-memory object representation of that data.
    with open(args.in_csv, "rb") as in_csv_file:
        csv_reader = csv.DictReader(in_csv_file, delimiter=",", quotechar='"')
        # row_num = 0
        for row in csv_reader:
            app_id = row[csv_key_app_id]
            hostname = row[csv_key_hostname]
            app_name = row[csv_key_app_name_from_web_store]
            package_name = row[csv_key_package_name]
            if row[csv_key_app_developer_oculus]:
                developer_name = row[csv_key_app_developer_oculus]
            else:
                developer_name = row[csv_key_app_developer_sidequest]
            app_package_name = row[csv_key_app_package]
            second_level_domain = row[csv_key_sld_label]
            policy_url = row[csv_key_policy_url]

            # turn hostname into sld
            if hostname not in hostname_to_sld:
                hostname_to_sld[hostname] = second_level_domain

            sld = second_level_domain
            key = get_ais_key(app_id,package_name)

            # Get existing AppInfo, if any, otherwise create new.
            ai = ais.get(key, DeviceAppInfo(app_id, app_name, package_name,
                                            developer_name, app_package_name, policy_url))
            # Associate hostname with app.
            ai.set_contacts_hostname(sld)

            # Update dict (in case we ended up creating a new AppInfo above)
            if key not in ais:
                ais[key] = ai

            # Update dict of hostname to DeviceAppInfo
            if sld not in hostname_to_apps:
                hostname_to_apps[sld] = []
            if ai not in hostname_to_apps[sld]:
                hostname_to_apps[sld].append(ai)
                if len(hostname_to_apps[sld]) > 1:
                    print("Found new app %s contacting sld %s, original hostname %s" % (ai.app_id, sld, hostname))

    print("Found %d App Infos for Device" % len(ais))

    # read in the file again to do the second time to label each row, and write it out as well
    with open(args.in_csv, "rb") as in_csv_file:
        csv_reader = csv.DictReader(in_csv_file, delimiter=",", quotechar='"')

        with open(args.out_csv, "wb") as out_csv_file:
            csv_writer = csv.writer(out_csv_file, encoding="utf-8")
            csv_header = csv_reader.fieldnames + [csv_key_party_label, csv_key_real_party_label]
            csv_writer.writerow(csv_header)

            # row_num = 0
            for row in csv_reader:
                app_id = row[csv_key_app_id]
                hostname = row[csv_key_hostname]
                app_name = row[csv_key_app_name_from_web_store]
                package_name = row[csv_key_package_name]
                if row[csv_key_app_developer_oculus]:
                    developer_name = row[csv_key_app_developer_oculus]
                else:
                    developer_name = row[csv_key_app_developer_sidequest]
                # Get existing AppInfo, if any, otherwise create new.
                key = get_ais_key(app_id, package_name)
                ai = ais.get(key)
                if not ai:
                    print("ERROR: could not find App info for %s, %s" + (app_id, app_name))
                    print("Skipping row " + hostname)
                    continue

                sld = hostname_to_sld[hostname]
                print("*******Getting party label for App %s, Developer %s, sld: %s, hostname: %s" % (ai.app_name, developer_name, sld, hostname))

                party_labels = get_party_labels(sld, ai, hostname)
                print("Party labels %s found for SLD %s" % (",".join(party_labels), sld))
                print("*******Done party label for App %s, Developer %s, sld: %s, hostname: %s" % (ai.app_name, developer_name, sld, hostname))

                # put into array by header order (ignoring the last column, since that is party_labels)
                data_row = [row[header_name] for header_name in csv_header[0:-2]]

                # add party label
                party_labels_merge_third_and_unknown = []
                for label in party_labels:
                    if label == UNKNOWN_PARTY:
                        party_labels_merge_third_and_unknown.append(THIRD_PARTY)
                    else:
                        party_labels_merge_third_and_unknown.append(label)

                data_row.append(";".join(party_labels_merge_third_and_unknown))

                # real party labels have unknowns
                data_row.append(";".join(party_labels))

                # write row
                csv_writer.writerow(data_row)
