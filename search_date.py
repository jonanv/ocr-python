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
        Today is 29th of May, 2020. In UK is written as 05/29/2020, or 5/29/2020 or you can even find it as 5/29/20. Instead of / you can either use - or . like 5-29-2020 or 5.29.2020. In Greece, the date format is dd/mm/yy, which means that today is 29/05/2020 and again we can use dots or hyphen between date parts like 29-05-20 or 29.05.2020. We can also add time, like 29/05/2020 19:30. Personally, my favorite date format is Y/mm/dd so, I would be happy to convert easily all these different dates to 2020/05/29
        entries are du 21-03-2021
        entries are du 19.04.2021
    '''

# matches = datefinder.find_dates(string_with_dates) # Format: 2021-10-22 18:30:00
matches = datefinder.find_dates(string_with_dates, source=True) # Format: (datetime.datetime(2021, 9, 19, 0, 0), '9/19')
for match in matches:
    print(match)