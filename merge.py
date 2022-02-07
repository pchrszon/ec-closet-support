#!/usr/bin/env python

import csv
import sys

import xlsxwriter

# reviewers: DBLP -> (name, institution, email)
# reviewers_list: [DBLP]
# reviewer_ids: DBLP -> id
# assignment: [(DBLP, pid)]


def write_row(worksheet, row, *cells):
    for (column, cell) in enumerate(cells):
        worksheet.write(row, column, cell)


def read_reviewer_table(filename, next_id, reviewers, reviewers_list, reviewer_ids, assignments):
    with open(filename, newline='') as file:
        file_reader = csv.reader(file, delimiter=";")
        for row in file_reader:
            # skip header if present
            if "#" in row[0]:
                continue

            try:
                pid, firstname, lastname, institution, email, dblp = int(row[0]), row[2].strip(), row[3].strip(), row[4].strip(), row[5].strip(), row[6].strip()
            except ValueError:
                continue

            name = firstname + " " + lastname

            # no reviewer given for paper
            if not dblp:
                continue

            # if reviewer is already known, do not add again, but check for consistency
            if dblp in reviewers:
                if reviewers[dblp][0] != name or reviewers[dblp][2] != email:
                    print("Inconsistent data for:", name, email)
                    print("Existing entry:       ", reviewers[dblp][0], reviewers[dblp][2], "\n")
            else:
                reviewers[dblp] = (name, institution, email)
                reviewers_list.append(dblp)
                reviewer_ids[dblp] = next_id
                next_id = next_id + 1

            assignments.append((dblp, pid))

    return next_id


def write_subreviewer_table(filename, reviewers, reviewers_list):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet("Sheet1")

    for (rid, dblp) in enumerate(reviewers_list):
        name, institution, email = reviewers[dblp]
        write_row(worksheet, rid, rid, name, institution, email, dblp)

    workbook.close()


def write_assignment_table(filename, reviewers, reviewer_ids, assignments):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet("Sheet1")

    for (i, (dblp, pid)) in enumerate(assignments):
        rid = reviewer_ids[dblp]
        name = reviewers[dblp][0]
        write_row(worksheet, i, rid, name, pid)

    workbook.close()


def main():
    reviewers = {}
    reviewers_list = []
    reviewer_ids = {}
    assignments = []

    next_id = 0
    for filename in sys.argv[1:]:
        next_id = read_reviewer_table(filename, next_id, reviewers, reviewers_list, reviewer_ids, assignments)

    write_subreviewer_table("subreviewers.xlsx", reviewers, reviewers_list)
    write_assignment_table("assignment.xlsx", reviewers, reviewer_ids, assignments)


if __name__ == "__main__":
    main()
