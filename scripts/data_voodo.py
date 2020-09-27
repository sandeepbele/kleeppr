
import csv
prod_letters = dict()
with open('/Users/sandeep/Documents/SB_Sources/Kleeppr-django/kleeppr4/runtime/db/newsletters.csv', newline='') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         is_complete = False
         #for a in ['letter','frequency', 'url', 'sender_email', 'author', 'desc' ]:
         for a in ['sender_email']:
             if row[a] is None or row[a] == "":
                 is_complete = True
                 break;
         if is_complete:
            prod_letters[row['letter']] = row

with open('/Users/sandeep/Documents/SB_Sources/Kleeppr-django/kleeppr4/runtime/db/dev_newsletters.csv',
          newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        key = row['letter']
        if key in prod_letters:
            print(row['letter'],row['frequency'],prod_letters[key]['url'],row['author'],prod_letters[key]['desc'])