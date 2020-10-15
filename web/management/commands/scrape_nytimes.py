from django.core.management.base import BaseCommand, CommandError
from bs4 import BeautifulSoup
from web.models import Publisher,Newsletters,Tags
import re

class Command(BaseCommand):

    def handle(self, *args, **options):

        freq_mapping = {

            "Daily":"D",
            "Three Times a Week" : "FW",
            "Weekdays":"D",
            "As Needed":"R",
            "Weekly":"W",
            "Twice a Week":"FW",
            "Bi-Weekly":"FM",
            "Monthly":"M",
            "Five Times a Week":"D",
        }

        with open ("/Users/sandeep/Documents/SB_Sources/Kleeppr-django/kleeppr4/tmp") as fp:

            css_soup = BeautifulSoup(fp.read(), 'html.parser')

            for category in css_soup.find_all(class_="css-1xn3edc"):
                cat = category.find(class_="css-1o0qd5y").text
                tags = []
                for c in re.split("and|&amp;|&",cat):
                    tag = Tags.objects.filter(tag=c).first()
                    if not tag:
                        tag = Tags(tag=c)
                        tag.save()

                    tags.append(tag)

                for section in category.find_all("div",class_="css-75vder"):
                    #print(section)
                    fre = section.find('p',class_="css-fsypem")
                    name = section.find('h3',class_="css-1icjac4")
                    desc = section.find('p',class_="css-10ve8v9")
                    if fre and name and desc:
                        print(fre.text ,name.text,desc.text)
                        fre = fre.text.strip()
                        name = name.text.strip()
                        desc = desc.text.strip()

                        publisher = Publisher.objects.filter(domain="nytimes.com").first()

                        newsletter = Newsletters.objects.filter(letter=name).first()
                        print(newsletter)
                        if not newsletter:
                            newsletter = Newsletters(letter=name)

                        newsletter.list_id='-'
                        newsletter.sender_email='nytdirect@nytimes.com'
                        newsletter.url='https://www.nytimes.com/newsletters'
                        newsletter.desc=desc
                        newsletter.author='The New York Times'
                        newsletter.author_url='https://www.nytimes.com'
                        newsletter.frequency=freq_mapping.get(fre)

                        newsletter.extra_info="None"
                        newsletter.is_active=True
                        newsletter.is_verified=True
                        newsletter.publisher=publisher

                        newsletter.save()
                        newsletter.tags.set(tags)
                        newsletter.save()
