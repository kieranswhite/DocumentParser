import re


def validate_brackets(string):
    match = ['()']
    string = re.sub("[^\(^\)]*", "", string)
    while any(x in string for x in match):
        for br in match:
            string = string.replace(br, '')
    return not string


## Based on page calculator in camelot with some tweaks
def calculate_pages(page_str, num_pages):

    # TODO  regex to clean out invalid content

    # remove spaces
    page_str = page_str.replace(" ", "")
    # validate pairs of brackets
    if validate_brackets(page_str):
        end = num_pages
        pages = []
        if page_str == "1":
            pages.append({"start": 1, "end": 1})
        elif page_str == "all":
            pages.append({"start": 1,"end": end})
        else:
            # replace keywords with values
            page_str = page_str.replace("end", str(end))

            # evaluate brackets and replace
            page_str = re.sub('\((.*?)\)', lambda m: str(eval(m.group())), page_str)

            # parse string split by , and - to calculate required pages
            for n in page_str.split(","):
                if "-" in n:
                    s, e = n.split("-")
                    pages.append({"start": int(s), "end": int(e)})
                else:
                    pages.append({"start": int(n), "end": int(n)})
        P = []
        for p in pages:
            P.extend(range(p["start"], p["end"] + 1))
        return sorted(set(P))
    else:
        raise Exception('Pages syntax: ' + page_str + ' was invalid. Please review the configuration')
