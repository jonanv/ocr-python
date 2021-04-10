import datefinder

string_with_dates = '''
        Central design committee session Tuesday 10/22 6:30 pm
        Th 9/19 LAB: Serial encoding (Section 2.2)
        There will be another one on December 15th for those who are unable to make it today.
        Workbook 3 (Minimum Wage): due Wednesday 9/18 11:59pm
        He will be flying in Sept. 15th.
        We expect to deliver this between late 2021 and early 2022.
        entries are due by January 4th, 2017 at 8:00pm
        created 01/15/2005 by ACME Inc. and associates.
    '''

matches = datefinder.find_dates(string_with_dates)
for match in matches:
    print(match)