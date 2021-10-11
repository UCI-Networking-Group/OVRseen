import unicodecsv as csv
import argparse
import tldextract


def _get_second_level_domain_from_tld(url_tld):
    return url_tld.domain + "." + url_tld.suffix


# =================== CSV column names ===================
csv_key_hostname = "hostname"
csv_key_sld_label = "second_level_domain"
keyset = [csv_key_hostname]
# ========================================================


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description="Given a csv with hostnames, we get the second level domain and append the information")
    ap.add_argument("in_csv", help="The expected column format and names should have " + str(keyset))
    ap.add_argument("out_csv", help="Output CSV where to write results.")

    args = ap.parse_args()

    hostname_to_sld = {}

    # Read data from CSV and create in-memory object representation of that data.
    with open(args.in_csv, "rb") as in_csv_file:
        csv_reader = csv.DictReader(in_csv_file, delimiter=",", quotechar='"')
        # row_num = 0
        for row in csv_reader:
            hostname = row[csv_key_hostname]


            # turn hostname into sld
            if hostname not in hostname_to_sld:
                tldresult = tldextract.extract(hostname)
                sld_new = _get_second_level_domain_from_tld(tldresult)
                hostname_to_sld[hostname] = sld_new

    # read in the file again to do the second time to label each row, and write it out as well
    with open(args.in_csv, "rb") as in_csv_file:
        csv_reader = csv.DictReader(in_csv_file, delimiter=",", quotechar='"')

        with open(args.out_csv, "wb") as out_csv_file:
            csv_writer = csv.writer(out_csv_file, encoding="utf-8")
            csv_header = csv_reader.fieldnames + [csv_key_sld_label]
            csv_writer.writerow(csv_header)

            # row_num = 0
            for row in csv_reader:
                hostname = row[csv_key_hostname]
                sld = hostname_to_sld[hostname]
                # put into array by header order (ignoring the last column, since that is second levle domain column)
                data_row = [row[header_name] for header_name in csv_header[0:-1]]

                #add sld
                data_row.append(sld)
                # write row
                csv_writer.writerow(data_row)
