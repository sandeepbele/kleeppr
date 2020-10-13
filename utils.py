import re, sys
from datetime import datetime, timezone
from bs4 import NavigableString, Tag
import io


def send_welcome_email():
    subject = 'Welcome to MyApp!'
    from_email = 'no-reply@myapp.com'
    to = instance.email
    plaintext = get_template('email/welcome.txt')
    html = get_template('email/welcome.html')

    d = Context({'username': instance.username})

    text_content = plaintext.render(d)
    html_content = html.render(d)

    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except BadHeaderError:
        return HttpResponse('Invalid header found.')


class StdoutToLogger(object):
    def __init__(self,_logger):
        self.terminal = sys.stdout
        self.logger = _logger
        self.buf_msg = ""

    def write(self, message):
        # in python 3, print takes list args .. code below waits for whole list
        if message == "\n":
            self.logger.info(self.buf_msg)
            self.buf_msg = ""
        else:
            self.buf_msg += message

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass


class MailUtils:

    def __init__(self):
        pass

    @staticmethod
    def get_x_time_ago(message_date):

        #date = message.get('Date')
        # Sun, 24 Feb 2019 18:53:01 +0000 (UTC)
        # fmt = "%a, %d %b %Y %X %z (%Z)"
        fmt = "%a, %d %b %Y %X %z"

        date = re.sub('\([A-Z]{3}\)', '', message_date).strip()
        d = datetime.strptime(date, fmt)

        now = datetime.now(timezone.utc)

        delta = now - d
        print(delta.total_seconds())

        total_secs = int(delta.total_seconds())

        secs_in_min = 60
        secs_in_hour = secs_in_min * 60
        secs_in_day = secs_in_hour * 24
        secs_in_week = secs_in_day * 7
        secs_in_month = secs_in_day * 30.5
        secs_in_year = secs_in_day * 365

        x_ago = ""

        if int(total_secs / secs_in_year) > 0:
            print(total_secs, secs_in_year, total_secs / secs_in_year)
            return date
        elif int(total_secs / secs_in_month) > 0:
            x_ago = "%d month(s) ago" % (int(total_secs / secs_in_month))
        elif int(total_secs / secs_in_week) > 0:
            x_ago = "%d week(s) ago" % (int(total_secs / secs_in_week))
        elif int(total_secs / secs_in_day) > 0:
            x_ago = "%d day(s) ago" % (int(total_secs / secs_in_day))
        elif int(total_secs / secs_in_hour) > 0:
            x_ago = "%d hour(s) ago" % (int(total_secs / secs_in_hour))
        elif int(total_secs / secs_in_min) > 0:
            x_ago = "%d minute(s) ago" % (int(total_secs / secs_in_min))
        else:
            x_ago = "%d second(s) ago" % int(total_secs)

        return x_ago

    @staticmethod
    def find_node_that_has_text(tag):
        #print(tag.name,tag.contents,type(tag.contents[0]),type(tag.contents[1]),len(tag.contents))
        has_text = False
        has_another_tag = False
        for child in tag.contents:
            if isinstance(child,NavigableString) and child.string != '\n':
                has_text = True
            elif isinstance(child,Tag):
                if has_text:
                    has_another_tag = True

        return has_text and has_another_tag


if __name__ == "__main__":

    from bs4 import BeautifulSoup

    msg = '''          <tr>
                    <td align=3D"center" style=3D"padding-bottom: 15px;col=
or: #686868;font-size: 14px;font-family: 'New York'=2C 'Times New Roman'=
=2C serif;-webkit-text-size-adjust: 100%;-ms-text-size-adjust: 100%;font-w=
eight: 300;mso-table-lspace: 0;mso-table-rspace: 0;" class=3D"padding-copy=
 appleLinks">
                      December 06=2C 2019
                    </td>
                  </tr> <tr>
                    <td align=3D"left" style=3D"padding: 0px 0px;-webkit-t=
ext-size-adjust: 100%;-ms-text-size-adjust: 100%;color: #000000;font-weigh=
t: 300;font-size: 18px;mso-table-lspace: 0;mso-table-rspace: 0;font-family=
: 'New York'=2C'Times New Roman'=2Cserif !important;" class=3D"padding-cop=
y">
                      <center>
                        <div style=3D"padding-bottom:0px;"><img alt=3D"600=
x300" border=3D"0" class=3D"emailImage" data-file-id=3D"2206689" height=3D=
"300" src=3D"https://gallery.mailchimp.com/4a77dae67a768bc3b920d4961/image=
s/fbaa463d-f8c3-482f-9479-a455e3ada08c.jpg" style=3D"border: 0px;display:=
 block;padding-bottom: 5px;width: 600px;height: 300px;margin: 0px;-ms-inte=
rpolation-mode: bicubic;line-height: 100%;outline: none;text-decoration: n=
one;padding-top: 15px;max-width: 100% !important;" width=3D"600"></div>
                        <span class=3D"image-caption" style=3D"font-size:=
 12px;text-align: right;display: block;line-height: 1.1;font-style: italic=
;color: #8B8A8A;font-family: 'New York'=2C'Times New Roman'=2Cserif !impor=
tant;">
                          <i><span>A moody winter sky</span>
                          </i>=C2=A0=C2=A0</span>
                        </center>

                        <hr mc:hideable=3D"hideable_4" style=3D"color:#5b5=
958;" mchideable=3D"hideable_4">
                      </td>
                    </tr><div class=3D"story-title" style=3D"color: #000000=
;line-height: 28px;font-size: 26px;font-weight: 600;padding-top: 25px !imp=
ortant;padding-bottom: 5px !important;">This week</div><div style=3D"padding-bottom:30px;">I&#39;ve been
 slowly making my way through Emily Wilson&#39;s 2017 English translation
 of <em>The Odyssey=2C </em>sometimes just a book a week. I received Wilso
n&#39;s translation as a gift this summer with a lovely inscription (note:
 did you miss last week&#39;s <a href=3D"https://annfriedman.us7.list-mana
ge.com/track/click?u=3D4a77dae67a768bc3b920d4961&id=3D7c66bef1a2&e=3D41855e517e" target=3D"_blank" style=3D"-webkit-text-size-adjust: 100%;-ms-text=
-size-adjust: 100%;color: #20927d;text-decoration: none;">giving guide</a>
?)=2C and it&#39;s been a reliable presence in the second half of my year.
 You may have heard about this version=2C because Wilson received a lot of
 deserved attention for her approach to the project: Rather than trying to
 remain faithful to every other written translation of this oral epic poem
=2C she aims to&nbsp;&quot;tell the old story for our modern times.&quot;<
br>
<br></div>'''

    soup = BeautifulSoup(msg, 'html.parser')
    txt_nodes = soup.find_all('p')
    txt = ""
    for txt_node in txt_nodes:
        txt += " " + txt_node.get_text().strip()
        if len(txt) > 600:
            break;

    if not txt:
        txt_nodes = soup.find_all(MailUtils.find_node_that_has_text)
        for txt_node in txt_nodes:
            txt += " " + txt_node.get_text().strip()
            if len(txt) > 600:
                break;

    #if not txt:
    #    txt = soup.get_text()

    print("-------------")
    print(txt[:600])
    # print(txt)
