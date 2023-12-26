from flask import Flask, render_template, request
import psycopg2
from datetime import datetime
import re

conn = psycopg2.connect(
    host="dpg-cm4gb4i1hbls73ademp0-a.singapore-postgres.render.com",
    port=5432,
    user="vitcc",
    password="BIY9sFDKjt33V4LdTOdRK7nzlSkTg8QW",
    database="libraryvit"
)

cur = conn.cursor()

app = Flask(__name__)

pen = 0
hol = 0
user = ''
temp = []
data_ = []
total = 0


@app.route('/')
def index():
    global pen,hol,user,temp,data_
    pen = 0
    hol = 0
    user = ''
    temp = []
    data_ = []
    total = 0
    return render_template('Student_Login.html')

@app.route('/availability')
def availability():
    global user
    if(user==''):
        return index()
    return render_template('student_Availability.html')

@app.route('/penalty')
def penalty():
    global user,temp,total
    if user=='':
        return index()
    elif temp==[]:
        total = 0
        cur.execute("select * from MyHoldings where reg_no = '{name}'".format(name = user))
                
        for i in cur:
            to_ = list(map(int,i[-1].split('-')))
            end = datetime(to_[-1],to_[-2],to_[-3])
            total_ = ((end-datetime.now()).days)
            if(total_<=0):
                temp.append([i[0],i[2],i[3],'2',str(abs(total_)),str(abs(total_)*2)])
                total+=(abs(total_)*2)

    return render_template('student_penalty.html',data = temp,total = str(total))

@app.route('/extension')
def extension():
    global user
    if(user==''):
        return index()
    return render_template('student_Extension.html')

@app.route('/extension_status')
def extensionStatus():
    global user
    if(user==''):
        return index()
    cur.execute("select * from extension where reg_no = '{}'".format(user))
    temp_exe = []
    for i in cur:
        temp_exe.append([i[0],i[2],i[3],i[-1]])
    return render_template('student_ExeReq_status.html',data = temp_exe)

@app.route('/extensionRequest',methods = ['GET'])
def extensionRequest():
    global user
    if user!='':
        x3 = request.args.get('name')
        x4 = request.args.get('auth')
        x5 = request.args.get('res')
        x6 = request.args.get('date')
        print(x3,x4,x5,x6)
        cur.execute("select * from myholdings where reg_no = '{}'".format(user))
        for i in cur:
            if i[2].lower().split(" ")==x3.lower().split(" ") and i[3].lower().split(" ")==x4.lower().split(" "):
                print("got a match")
                date_check = re.match('[0-9]?[0-9]-[0-1]?[0-9]-[0-9][0-9][0-9][0-9]',x6)
                if(date_check) and int(x6.split('-')[1])<=12:
                    try:
                        cur.execute("insert into extension values('{}','{}','{}','{}','{}','{}','pending')".format(i[0],i[1],i[2],i[3],x5,x6))
                        conn.commit()
                        return render_template('student_Extension_True.html')
                    except:
                        conn.rollback()
                        return render_template('student_Extension_Message.html')
                else:
                    return render_template('student_Extension_wrong_date.html')
        return render_template('student_Extension_False.html')
    else:
        return index()

@app.route('/availableStatus',methods=['POST'])
def availableStatus():
    book = request.form.get('bookname')
    auth = request.form.get('authorname')
    fin_rel = []
    cur.execute('select * from Availability')
    for i in cur:
        if book.lower()==i[0].lower() and auth.lower()==i[1].lower() and i[3]=='TRUE':
            return render_template('student_available_True.html',i = i[2])
        elif (book or auth) and (book.lower() in i[0].lower() or book=='') and (auth.lower() in i[1].lower() or auth=='') and i[3]=='TRUE':
            fin_rel.append([i[0],i[1],i[2]])
    if fin_rel!=[]:
        return render_template('student_availability_rel.html',data = fin_rel)
    elif (book =='' and auth==''):
        return render_template('student_available_Invalid.html')
    else:
        return render_template('student_available_False.html')


@app.route('/holdings')
def holdings():
    global user,data_
    if user=='':
        return index()
    elif data_==[]:
        cur.execute("select * from MyHoldings where reg_no = '{name}'".format(name = user))
            
        for i in cur:
            for_ = list(map(int,i[-2].split('-')))
            to_ = list(map(int,i[-1].split('-')))
            start = datetime(for_[-1],for_[-2],for_[-3])
            end = datetime(to_[-1],to_[-2],to_[-3])
            data = list(i)
            x = (end-start).days
            data.append(x)
            data.append((end-datetime.now()).days)
            data_.append(data)
            print(data)
    return render_template('student_MyHoldings.html',data = data_)

@app.route('/student', methods=['POST'])
def process_form():
    global user
    cur.execute('select * from Student')
    # Access form data using request.form
    name = request.form.get('ID')
    password = request.form.get('pass')
    user = name
    for i in cur:
        if i[0]==name and i[1] == password:
            
            return holdings()
        
        else:
    # Process the data (e.g., print it)
            return f"Form submitted successfully! Name: {name}, Age: {password}"

if __name__ == '__main__':
    app.run(debug=True)
