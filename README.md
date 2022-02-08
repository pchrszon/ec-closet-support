# Conflict-of-Interest Detection using CLOSET and Easy Chair

Handling conflicts of interest (CoI) is an integral part of the reviewing
process for journal and conference submissions. CoI can be detected
automatically using the
[CLOSET](https://personal.ntu.edu.sg/assourav/research/DARE/closet.html) tool.
The scripts in this repository support this CoI detection process for conferences
that

- have a sizable number of submissions and PC members that render manual checking
  difficult,
- use a double-blind reviewing policy,
- allow the PC members to delegate some submissions to subreviewers, and
- use Easy Chair for the conference management.

CoI checking in this scenario is difficult, since authors generally cannot
declare CoI with subreviewers at submission time as the subreviewers may not
be known before the reviewing process begins. On the other hand, the PC members
cannot check for CoI between the authors of a submission and the subreviewers
as they must not know the author names. This issue is resolved by delegating the
CoI checking to CLOSET. In particular, the workflow is as follows.

1. The conference chair assigns submissions to PC members for review as usual.
2. The PC members may select one or more potential subreviewers for their
   assigned submissions.
3. Using CLOSET, CoI between the authors of the submissions and their assigned
   subreviewers are detected.
4. PC members receive feedback on whether a subreviewer has a CoI with the
   authors of an assigned submission or not. The PC members may then proceed to
   request reviews from subreviewers without a CoI.

Each step of this workflow is described in detail in the following.


## Prerequisites

For running the scripts, a Python 3 installation is required. Furthermore,
the `xlsxwriter` package must be installed. This can be achieved using the
following command:

```
pip install xlsxwriter --user
```


## Workflow

Before starting the process that is described in the following, make sure that
the submissions have been assigned to the PC members for review.


### Collect subreviewer candidates from PC members

Each PC member may select one or more potential subreviewers per submission. In
order to streamline this process, the `generate.py` script may be used. It
generates a personalized Excel table for each PC member that already contains
all submissions that have been assigned to the respective PC member. This table
also contains the columns that need to be filled in by the PC member, namely
the name, email address, and [DBLP](dblp.org) page of the potential
subreviewers.

The `generate.py` scripts requires the following input files which can be
obtained from Easy Chair. Note that downloading these files requires that you
are logged in as the conference chair.

1. The list of reviewers. In the Easy Chair menu bar, select "Assignment",
   "Download in CSV". Then, from the table, download `reviewer.csv`.
2. In the same table, download `assignment.csv`.
3. In the menu bar, select "Submissions". Then, choose "Submissions in Excel"
   from the top right menu. Open the downloaded file in Excel and then save
   it as a CSV file (using File > Save as ... and then choose `*.csv` as file
   type in the save dialog).

After obtaining these files, the script can be invoked using the following
command (you may need to adapt the filenames or paths depending on where you
have saved the files):

```
./generate.py reviewer.csv assignment.csv submissions.csv
```

This will generate an Excel table for each PC member with the columns
"submission ID", "title", "first name", "last name", "email address", and
"dblp page". You may now distribute these tables to the PC members. Note that
a PC member can propose multiple subreviewers for a single submission by
duplicating the row of the respective submission.


### Checking for CoI using CLOSET

If you have received the subreviewer proposals from the PC members, the next
step is preparing the data for CoI checking with CLOSET. For this, two steps
are required.

1. Convert the (partially) filled subreviewer tables into CSV format using
   Excel and put them into a designated directory, e.g., named `subreviewers`.
2. Use the `merge.py` script to combine the subreviewer tables and to convert
   them into the format required by CLOSET.

   ```
   ./convert.py subreviewers/*.csv
   ```

   This will generate two files. The file `subreviewers.xlsx` contains the list
   of all proposed subreviewers, and `assignment.xlsx` defines the assignment of
   subreviewers to submissions.
   In case a subreviewer has been proposed multiple times, the script will check
   whether the provided data is consistent over all entries.


Finally, download the conference data (in Excel format) in Easy Chair by
selecting "Premium" and then "Conference data download" from the menu. You may
now send off the conference data Excel file, the `subreviewers.xlsx` file, and
the `assignment.xlsx` file for CoI checking using CLOSET.


### Provide feedback to PC members

After CoI checking using CLOSET, you should have received at least two Excel
files, one containing authorship conflicts (named `CoiPC-*.xlsx`) and another
containing institutional conflicts (named `CoiInst-*.xlsx`). Convert the Excel
files into CSV format using Excel and save them as `CoiPC.csv` and
`CoiInst.csv`, respectively.

Using the `feedback.py` script, the filled subreviewer tables obtained from the
PC members can now be annotated with the results of the CoI check. Assuming the
subreviewer tables in CSV format are still contained in the `subreviewers`
directory, execute the following command:

```
./feedback.py CoiPC.csv CoiInst.csv subreviewers/*.csv
```

This will generate a new Excel table for each subreviewer containing one
additional new column named "conflict of interest". You may now distribute these
tables to the PC members.

Note that some conflicts are caused by a co-authorship of the subreviewer
and the submission authors from more than 2 years ago. These are marked
separately.

If some of the entries of the CoI results could not be matched with any row in
the subreviewer tables, the script will issue a warning. This is usually caused
by, e.g., accents or umlauts in the author names and may be fixed by either
amending the result tables or the subreviewer tables.


## Schema information

This section lists the schema of each data file consumed by the scripts. The
scripts do not perform any schema validation. If you encounter errors or
unexpected output, please check if your input data has the right format.

* `generate.py`

    - `reviewer.csv` (separator: `,`): PC member ID, name, mail address, role
    - `assignment.csv` (separator: `,`): PC member ID, submission ID
    - `submissions.csv` (separator: `;`): submission ID, authors, title, ...

* `merge.py`

    - subreviewer table (separator: `;`): submission ID, title, first name, last name, email address, dblp page

* `feedback.py`

    - `CoiPC.csv` (separator: `;`): author, (meta)reviewers, submission ID, history
    - `CoiInst.csv` (separator: `;`): submission ID, authors, (meta)reviewers
