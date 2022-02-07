#!/usr/bin/env python

import csv
import sys
import xlsxwriter


def read_reviewers(filename):
    result = {}

    with open(filename, newline='') as reviewers_file:
        reviewers_reader = csv.reader(reviewers_file, delimiter=",")
        for row in reviewers_reader:
            rid, name = int(row[0]), row[1].strip()
            result[rid] = name

    return result


def read_paper_titles(filename):
    result = {}

    with open(filename, newline='') as papers_file:
        papers_reader = csv.reader(papers_file, delimiter=";")
        for row in papers_reader:
            try:
                pid, title = int(row[0]), row[2].strip()
                result[pid] = title
            except ValueError:
                pass

    return result


def read_assignment(filename):
    result = {}

    with open(filename, newline='') as assign_file:
        assign_reader = csv.reader(assign_file, delimiter=",")
        for row in assign_reader:
            rid, pid = int(row[0]), int(row[1])
            result.setdefault(rid, []).append(pid)

    return result


def create_tables(reviewers, papers, assignment):
    for (rid, pids) in assignment.items():
        pids.sort()

        reviewer = reviewers[rid]
        filename = reviewer.replace(" ", "_") + ".xlsx"

        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet(reviewer)

        header_format = workbook.add_format()
        header_format.set_bold()

        header = ["#", "title", "first name", "last name", "institution", "email address", "dblp page"]
        for i, col_header in enumerate(header):
            worksheet.write(0, i, col_header, header_format)

        start_idx = 1
        width = 1
        for index, pid in enumerate(pids):
            title = papers[pid]
            width = max(width, len(title))

            worksheet.write(index + start_idx, 0, pid)
            worksheet.write(index + start_idx, 1, title)

        worksheet.set_column(0, 0, 5)
        worksheet.set_column(1, 1, width * 0.8)

        workbook.close()


def main():
    if len(sys.argv) != 4:
        print("Usage:", sys.argv[0], "<REVIEWERS.CSV> <ASSIGNMENT.CSV> <SUBMISSIONS.CSV>")
        return 1

    reviewers = read_reviewers(sys.argv[1])
    papers = read_paper_titles(sys.argv[3])
    assignment = read_assignment(sys.argv[2])

    create_tables(reviewers, papers, assignment)


if __name__ == "__main__":
    main()
