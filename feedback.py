#!/usr/bin/env python

import csv
import datetime
import re
import os
import sys

import xlsxwriter


MAX_CONFLICT_AGE = 2


CONFLICT = 0
NO_CONFLICT = 1
OLD_CONFLICT = 2


CURRENT_YEAR = datetime.datetime.now().year

RE_YEAR = re.compile(r'\[\((\d+),')

# conflicts: paper id -> [(reviewer, year, found)]

def write_row(worksheet, row, *cells):
    for (column, cell) in enumerate(cells):
        worksheet.write(row, column, cell)


def parse_reviewer_name(cell):
    return cell.split('(')[0].strip()


def parse_publication_year(cell):
    m = RE_YEAR.search(cell)
    if m:
        return int(m.group(1))
    else:
        return None


def read_authorship_conflicts(filename, conflicts):
    with open(filename, newline='') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            try:
                pid, reviewer = int(row[2]), parse_reviewer_name(row[1])
                conflicts.setdefault(pid, []).append([reviewer, parse_publication_year(row[3]), False])
            except ValueError:
                pass


def read_institutional_conflicts(filename, conflicts):
    with open(filename, newline='') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            try:
                pid, reviewer = int(row[0]), parse_reviewer_name(row[2])
                conflicts.setdefault(pid, []).append([reviewer, None, False])
            except ValueError:
                pass


def read_subreviewer_table(filename):
    result = []

    with open(filename, newline='') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            try:
                pid, title, firstname, lastname, institution, email, dblp = int(row[0]), row[1], row[2].strip(), row[3].strip(), row[4], row[5], row[6]
                result.append([pid, title, firstname, lastname, institution, email, dblp])
            except ValueError:
                pass

    return result


def annotate_subreviewer_table(table, conflicts):
    for row in table:
        pid, firstname, lastname = row[0], row[2], row[3]
        reviewer = (firstname + ' ' + lastname).lower()

        annotation = NO_CONFLICT
        if pid in conflicts:
            conflicting_reviewers = conflicts[pid]
            for item in conflicting_reviewers:
                if item[0] == reviewer:
                    item[2] = True # we have found a match in the subreviewer table
                    if item[1] and CURRENT_YEAR - item[1] > MAX_CONFLICT_AGE and annotation != CONFLICT:
                        annotation = OLD_CONFLICT
                    else:
                        annotation = CONFLICT

        row.append(annotation)


def write_subreviewer_table(filename, table):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet("Sheet1")

    standard_format = workbook.add_format()
    conflict_format = workbook.add_format()
    conflict_format.set_bold()
    conflict_format.set_font_color('red')


    write_row(worksheet, 0, "#", "title", "first name", "last name", "institution", "email address", "dblp page", "conflict of interest")

    for i, row in enumerate(table):
        annotation = row[-1]
        if annotation == NO_CONFLICT:
            annot_text = "no"
        elif annotation == CONFLICT:
            annot_text = "yes"
        else:
            annot_text = "yes, but more than " + str(MAX_CONFLICT_AGE) + " years ago"

        if annotation == CONFLICT:
            annot_format = conflict_format
        else:
            annot_format = standard_format

        write_row(worksheet, i + 1, *(row[:-1]))
        worksheet.write(i + 1, 7, annot_text, annot_format)

    workbook.close()


def main():
    auth_conflict_filename, inst_conflict_filename = sys.argv[1], sys.argv[2]

    conflicts = {}
    read_authorship_conflicts(auth_conflict_filename, conflicts)
    read_institutional_conflicts(inst_conflict_filename, conflicts)

    for subreviewers_filename in sys.argv[3:]:
        table = read_subreviewer_table(subreviewers_filename)
        annotate_subreviewer_table(table, conflicts)

        basename, _ = os.path.splitext(subreviewers_filename)
        filename = basename + ".xlsx"

        write_subreviewer_table(filename, table)

    for pid, conflicting_reviewers in conflicts.items():
        for item in conflicting_reviewers:
            if not item[2]:
                print("No match found for", item[0], "(paper ID", pid, ")")


if __name__ == "__main__":
    main()
