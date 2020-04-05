import csv
import sys
import copy
import argparse


def read_csv(path,*fields, rows_with_fieldnames=True):
    """ Read CSV As a Whole
    """
    with open(path, newline="", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader]

        if fields:
            cols = tuple([r[fd] for r in rows] for fd in fields if fd in reader.fieldnames)
#            print("type(cols):", type(cols), "type(fields)",type(fields))
            if len(cols) == len(fields) == 1:
                # outer variable could recieve a list, not tuple with a list as the single element
                return cols[0]
            elif len (cols) == len(fields):
                return cols
            else:
                raise ValueError("Invalid fields:{}.".format(",".join(list(filter(lambda x:x not in reader.fieldnames)))))
        elif rows_with_fieldnames:
            return rows, reader.fieldnames
        else:
            return rows


def write_csv(pth, rows, fieldnames):
    with open(pth, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames = fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def merge_by(
    dreader1,
    fieldnames1,
    dreader2,
    fieldnames2,
    key,
    **kwargs
):
    """ Merge two csv files
    """

    if key not in fieldnames1 or key not in fieldnames2:
        raise ValueError("Invalid key:{}".formqat(key))

    # Note: nrows of merged csv = nrows of dreader1
    merged = { r1[key]:r1 for r1 in dreader1 }

    # fieldnames appended to fieldnames1 list
    # preference with same fieldname: dreader1 > dreader2
#    print("fn1=",fieldnames1,"fn2=",fieldnames2)
    appdfn = [f2 for f2 in fieldnames2 if f2 not in fieldnames1]
#    print("APPDFN=",appdfn)
    for r2 in dreader2:
        if r2[key] in merged: # shared key
            r1 = merged[r2[key]]
            r3 = copy.deepcopy(r1)
            for fn in appdfn: # append new fields
                if fn in r3:
                    raise ValueError("Duplicately set field {} at key {} ".format(fn, r2[key]))
                else:
                    r3[fn] = r2[fn]
        
            for fn, functor in kwargs.items(): # fieldnames 
                r3[fn] = functor(r1, r2)

            merged[r2[key]] = r3 # update 
            del r1

    # no need for the key
    merged = [v for k,v in merged.items()]
    fieldnames3 = fieldnames1 + appdfn

    return merged, fieldnames3


def merge_csv(key, out_pth, csv_path1, csv_path2, *pths):
    first, fn1 = read_csv(csv_path1)
    second, fn2 = read_csv(csv_path2)
    remain = list(pths)
    while first and second:
        first, fn1 = merge_by(first, fn1, second, fn2, key)
        second, fn2 = read_csv(remain.pop(0)) if remain else ([], [])

    write_csv(out_pth, first, fn1)


def parse_args(args):
    parser = argparse.ArgumentParser(description='Simple script to help to merge several csv files')
    parser.add_argument("csvout", metavar="CSVOUT",
                        help="Where to place the merged csv file.")
    parser.add_argument("csvpths", metavar='CSVPTH', nargs='+',
                        help="Multiple csv paths stored pieces of information. The former CSVPTH arguemnts will get higher priority.")
    parser.add_argument('--key', default="asin",
                        help="criteria to merge records, by default set to 'asin'.")

    return parser.parse_args(args)


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    args = parse_args(args)

    if len(args.csvpths) == 1:
        raise ValueError("More than one CSVPTH arguemnts are required.")

#    pths = args.csvpths
#    print("args.csvout=",args.csvout,"args.csvpths=",args.csvpths)
    merge_csv(args.key, args.csvout, *args.csvpths)

if __name__ == "__main__":
    main()
