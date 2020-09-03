from flask import render_template, Blueprint, current_app, g, redirect, url_for
from db import get_db
import csv
import os.path
from auth import login_required

bp = Blueprint('website', __name__, url_prefix='/')

@bp.route('/app')
def mob():
    if g.user is None:
        return render_template("register-mobapp.html")
    else:
        return redirect(url_for('mailbox.user_feed'))

@bp.route('/')
def index():
    if 'user' not in g or ( g.user is None or g.user.is_anonymous):
        return render_template("landing.html")
    else:
        return redirect(url_for('mailbox.user_feed'))

@bp.route('/onreset')
def onreset():
    return render_template('onreset.html')

@bp.route('/bookmark')
@login_required
def bookmark():
    return render_template('bookmarklet.html')

@bp.route('/explore2', defaults={'c':None, 'start_row':2, 'rows_to_return':20 } )
#@bp.route('/explore?s=<start_row:int>',defaults={'rows_to_return':20})
#@bp.route('/explore?r=<rows_to_return:int>',defaults={'start_row':1})
#@bp.route('/explore?s=<start_row:int>&r=<rows_to_return:int>')

def explore2(c=None, start_row=2,rows_to_return=20, no_feed_reminder=False):

    letters_csv = current_app.config['LETTERS_CSV']

    if start_row < 2:
        start_row = 2

    if rows_to_return < 0 :
        rows_to_return = 20

    end_row = (start_row - 1) + rows_to_return

    print(start_row,end_row)
    prev = start_row
    next = end_row + 1

    results = list()
    fieldnames = ('letter','url','desc','author','author_url', 'frequency', 'tags')

    with open( os.path.join(current_app.instance_path,letters_csv), newline='') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=fieldnames, delimiter=',')

        for row in reader:
            #print(row, reader.line_num)
            print(start_row, reader.line_num, end_row)
            if start_row <= reader.line_num <= end_row:
                results.append(row)
                print(results)

            if reader.line_num >= end_row:
                break;

        if reader.line_num < end_row:
            next = -1

    return render_template("explore.html", cards=results, next=next, prev=prev, no_feed_reminder=no_feed_reminder);

@bp.route('/explore/<tag>/<int:page_no>')
@bp.route('/explore/<int:page_no>',defaults={'tag':'all'})
@bp.route('/explore/<tag>', defaults={'page_no':1})
@bp.route('/explore',defaults={'page_no':1,'tag':'all'})
@login_required
def explore(page_no,tag, no_feed_reminder=False):

    page_size = 5
    params=[]

    query = "select * from newsletters"
    if tag != "all":
        query += " where tags=?"
        params.append(tag)

    query += " limit ? offset ?"
    params.append(page_size)
    params.append((page_no-1)*page_size)

    db = get_db()
    newsletters = db.execute(
        query, ( params )
    ).fetchall()

    if (len(newsletters) < page_size):
        next = -1
    else:
        next = page_no + 1

    if page_no == 1:
        prev = -1
    else:
        prev = page_no - 1


    tags_query = "select DISTINCT tags from newsletters where tags NOTNULL and tags !=''"
    tags = db.execute(
        tags_query
    ).fetchall()


    return render_template("explore.html", cards=newsletters, tags=tags, selected_tag=tag,
                           next=next, prev=prev, no_feed_reminder=no_feed_reminder);
