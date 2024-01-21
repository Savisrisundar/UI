from flask import Flask, render_template, request
import psycopg2
from datetime import datetime
import random
import smtplib
from email.mime.text import MIMEText

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

credential_status = True
email = ''
gen_otp = 0

admin_user = ''



def send_email(subject, body, to_email):
    # Your email credentials
    sender_email = "vitlibrary1984@gmail.com"
    sender_password = "keyy ktji xdqw regm"

    # Email content
    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = to_email

    # Establish a connection to the SMTP server
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        
        # Login to your email account
        server.login(sender_email, sender_password)
        
        # Send the email
        server.sendmail(sender_email, to_email, message.as_string())




@app.route('/')
def index():
    global pen,hol,user,temp,data_,credential_status,gen_otp,email,admin_user
    pen = 0
    hol = 0
    user = ''
    temp = []
    data_ = []
    total = 0
    credential_status = True
    gen_otp=0
    email=''
    admin_user=''
    return render_template('Student_Login.html')

@app.route('/availability')
def availability():
    global user,credential_status

    if(user=='' and credential_status):
        return index()
    return render_template('student_Availability.html')

@app.route('/penalty')
def penalty():
    global user,temp,total
    if user=='' and credential_status:
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
    if(user=='' and credential_status):
        return index()
    return render_template('student_Extension.html',request_accepted=3)

@app.route('/extension_status')
def extensionStatus():
    global user
    if(user=='' and credential_status):
        return index()
    cur.execute("select * from extension where reg_no = '{}'".format(user))
    temp_exe = []
    for i in cur:
        temp_exe.append([i[0],i[2],i[3],i[6]])
    return render_template('student_ExeReq_status.html',data = temp_exe)

@app.route('/extensionRequest',methods = ['GET'])
def extensionRequest():
    global user
    if user=='' and credential_status:
        return index()
    else:
        x3 = request.args.get('name')
        x4 = request.args.get('auth')
        x5 = request.args.get('res')
        x6 = request.args.get('date')

        

        print(x3,x4,x5,x6)
        cur.execute("select * from myholdings where reg_no = '{}'".format(user))
        for i in cur:
            if i[2].lower().split(" ")==x3.lower().split(" ") and i[3].lower().split(" ")==x4.lower().split(" "):
                try:
                    to_ = list(map(int,x6.split('-')))
                    end = datetime(to_[0],to_[1],to_[2])
                except:
                    return render_template('student_Extension.html',request_accepted=0)
                to_1 = list(map(int,i[5].split('-')))
                start = datetime(to_1[-1],to_1[-2],to_1[-3])
                days = (end-start).days
                print("got a match")
                print("insert into extension values('{}','{}','{}','{}','{}','{}','pending','{}')".format(i[0],i[1],i[2],i[3],x5,x6,days))
                try:
                    cur.execute("insert into extension values('{}','{}','{}','{}','{}','{}','pending','{}')".format(i[0],i[1],i[2],i[3],x5,x6,days))
                    conn.commit()
                    return render_template('student_Extension.html',request_accepted=1)
                except:
                    conn.rollback()
                    return render_template('student_Extension.html',request_accepted=0)
        return render_template('student_Extension.html',request_accepted = 0)


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
    if user=='' and credential_status:
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
    global user,credential_status
    cur.execute('select * from Student')
    # Access form data using request.form
    name = request.form.get('ID')
    password = request.form.get('pass')
    print(password)
    user = name
    for i in cur:
        if i[0]==name and i[1] == password:

            credential_status = False
            return holdings()
        
        
    user=''
    return "wrong data found"

        
@app.route('/forget_password')
def forget_pass():
    return render_template('student_forget_pass.html')

@app.route('/resend_otp')
def resend():
    global gen_otp,email
    gen_otp=random.randint(100000,999999)
    subject = "One time password"
    body = "your one time password for changing password   "+str(gen_otp)
    recipient_email = email
    send_email(subject, body, recipient_email)
    return enter_otp()

@app.route('/get_otp', methods=['POST'])
def get_otp():
    global gen_otp,email,user
    field1 = request.form.get('reg_no')
    field2 = request.form.get('mail')
    cur.execute("select name,email from student")
    for i in cur:
        if i[0]==field1 and i[1]==field2:
            user=field1
            email=field2
            gen_otp=random.randint(100000,999999)
            subject = "One time password"
            body = "your one time password for changing password   "+str(gen_otp)
            recipient_email = email
            send_email(subject, body, recipient_email)
            return enter_otp()
        
    return "User not found"

@app.route('/enter_otp')
def enter_otp():
    return render_template('student_OTP_check.html')
    

@app.route('/check_otp',methods = ['POST'])
def check_otp():
    global gen_otp,email,user
    otp = request.form.get('otp')
    if gen_otp==int(otp) and gen_otp!=0 and user!='':
        gen_otp=0
        return render_template('student_new_pass.html')
    else: return index()

@app.route('/new_student')
def new1():
    return render_template('student_new_pass,html')

@app.route('/change_password', methods=['POST'])
def change():
    global user
    field1 = request.form.get('pass1')
    field2 = request.form.get('pass2')

    if field1!=None and (field1==field2):
        cur.execute("update student set password = '"+str(field1)+"' where name = '"+user+"'")
        conn.commit()
        subject = "Your Password changed successfully"
        body = "your password for library dashboard has been changed successfully \n\n USER NAME = "+user+"\nPassword = "+field1+"\n\n use the above credential to access the webpage"
        recipient_email = email
        send_email(subject, body, recipient_email)
        return index()
    else:
        return new1()

    

#______________________________________________________________________________________________________________#
@app.route('/admin')
def admin():
    global admin_user,admin_email
    admin_email=''
    admin_user=''
    return render_template("Admin_Login.html")



@app.route('/resend_admin')
def resend_admin():
    global gen_otp,admin_email,admin_user
    if admin_email=='' or admin_user=='':
        return admin()
    gen_otp=random.randint(100000,999999)
    subject = "One time password"
    body = "your one time password for changing password   "+str(gen_otp)
    recipient_email = admin_email
    send_email(subject, body, recipient_email)
    return otp_admin()

@app.route('/admin_fp')
def admin_forget_pass():
    return render_template('Admin_forget_pass.html')

@app.route('/send_otp',methods = ['POST'])
def send_otp():
    global admin_user,admin_email,gen_otp
    name = request.form.get('EMP_ID')
    mail = request.form.get('mail-id')
    cur.execute("select name,email from admin")
    for i in cur:
        if i[0]==name and i[1]==mail:
            admin_user=name
            admin_email=mail
            gen_otp=random.randint(100000,999999)
            subject = "One time password"
            body = "your one time password for changing password   "+str(gen_otp)
            recipient_email = mail
            send_email(subject, body, recipient_email)
            return otp_admin()
            
    return 'Invalid data'

@app.route('/enter_admin_otp')
def otp_admin():
    return render_template('Admin_opt_check.html')

@app.route('/check_admin_otp',methods=['POST'])
def check_admin_otp():
    global gen_otp,admin_user
    otp = request.form.get('otp')
    if admin_user=='':
        return admin()
    elif otp==str(gen_otp):
        return render_template('Admin_new_pass.html')
    else:
        return 'Wrong otp'

@app.route('/new_password')
def new():
    return render_template('Admin_new_pass.html')

@app.route('/password_change_admin',methods=['POST'])
def password_change_admin():
    global admin_user
    field1 = request.form.get('pass1')
    field2 = request.form.get('pass2')

    if field1!=None and (field1==field2):
        cur.execute("update admin set password='"+field1+"' where name='"+admin_user+"'")
        conn.commit()
        return render_template('Admin_Login.html')

    else:
        print(field1,field2)
        return new()
    
@app.route('/request_admin')
def request_admin():
    global admin_user
    if admin_user=='':
        return admin()
    cur.execute("select * from extension")
    data = []
    for i in cur:
        data.append([i[0],i[1],i[2],i[3],i[4],i[7]])
    return render_template('Admin_req.html',data = data)

@app.route('/admin_check',methods=['POST'])
def admin_check():
    global admin_user
    cur.execute('select name,password from admin')
    # Access form data using request.form
    name = request.form.get('ID')
    password = request.form.get('pass')

    for i in cur:
        if i[0]==name and i[1] == password:
            admin_user = name
            return request_admin()
    return render_template("Admin_Login.html")


@app.route('/penalty_admin')
def penalty_admin():
    if admin_user=='':
        return admin()
    cur.execute("select * from myholdings")
    data_to_html = []
    data_temp = list(cur)
    for i in data_temp:
        to_ = list(map(int,i[-1].split('-')))
        end = datetime(to_[-1],to_[-2],to_[-3])
        total_ = ((end-datetime.now()).days)
        if(total_<=0):
            data_to_html.append([i[0],i[1],i[2],i[3],str(abs(total_)),'2',str(abs(total_)*2)])
    return render_template('Admin_penalty.html',data = data_to_html)

@app.route('/book_data_admin')
def book_data_admin():
    if admin_user=='':
        return admin()
    return render_template('Admin_Book_data.html')
@app.route('/bood_data_show',methods = ['POST'])
def book_data_show():
    if admin_user=='':
        return admin()
    book_name = request.form.get('book')
    author_name = request.form.get('author')
    cur.execute(f"select * from myholdings")
    data_temp = []
    for i in cur:
        if(book_name.lower() in i[2].lower()) and (author_name!=None and author_name.lower() in i[3].lower()):
            data_temp.append(i)
    return render_template('Admin_Book_data_check_status.html',data= data_temp )

@app.route('/student_data_check_admin')
def student_data_check_admin():
    if admin_user=='':
        return admin()
    return render_template('Admin_Student_data.html')

@app.route("/student_data_admin/show",methods=['POST'])
def student_data_show():
    if admin_user=='':
        return admin()
    x=request.form.get('reg_no')
    cur.execute(f"select * from myholdings where reg_no='{x}';")
    data_temp = []
    for i in cur:
        to_ = list(map(int,i[5].split('-')))
        end = datetime(to_[-1],to_[-2],to_[-3])
        total_ = ((end-datetime.now()).days)
        data_temp.append([i[0],i[2],i[3],total_,str(abs(total_)*2) if total_<0 else 0])
    return render_template('Admin_stu_data_check_status.html',data = data_temp)

@app.route('/req_acccept')
def req_acccept():
    if admin_user=='':
        return admin()
    data_from_url = request.args.get('data')
    cur.execute(f"select date,reg_no from extension where serial_no='{data_from_url}'")
    x1 = list(cur)[0]
    reg_no_temp = x1[-1]
    x = x1[0]
    check_out = x[8:10]+'-'+x[5:7]+'-'+x[0:4]
    cur.execute(f"update myholdings set check_out = '{check_out}' where S_No='{data_from_url}'")
    conn.commit()
    cur.execute(f"delete from extension where serial_no='{data_from_url}'")
    conn.commit()
    cur.execute(f"select email from student where name='{reg_no_temp}'")
    email = list(cur)[-1][-1]
    sub = 'Book extension request'
    cont = 'Your Extension request on Book Serial Number : '+data_from_url+' has been accepted.'+'\n'+'check your website for further details'

    send_email(sub,cont,email)
    return request_admin()

@app.route('/req_reject')
def req_reject():
    if admin_user=='':
        return admin()
    data_from_url = request.args.get('data')
    cur.execute(f"select reg_no from extension where serial_no='{data_from_url}'")
    x1 = list(cur)
    reg_no_temp = x1[-1][-1]
    cur.execute(f"delete from extension where serial_no='{data_from_url}'")
    conn.commit()
    cur.execute(f"select email from student where name='{reg_no_temp}'")
    email = list(cur)[-1][-1]
    sub = 'Book extension request'
    cont = 'Your Extension request on Book Serial Number : '+data_from_url+' has been rejected. '+'\n'+'check your website for further details'

    send_email(sub,cont,email)
    return request_admin()




if __name__ == '__main__':
    app.run(debug=True)
