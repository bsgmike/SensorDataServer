

from multiprocessing import Process, Queue
from bottle import route, run, request, response
from bottle import static_file
import random, argparse
# import RPi.GPIO as GPIO
from time import sleep
# import Adafruit_DHT
import serial
import sys, select, os

@route('/hello')
def hello():
    return "Hello Bottle World!"



@route('/bstest1')
def bstest():
    return static_file('bstest_1.html', root='.')

@route('/plot3')
def plot3():
    return static_file('plot3.html', root='.')

@route('/original_plot')
def original_plot():
    return static_file('original_plot.html', root='.')


@route('/<filename:re:.*\.js>')
def javascripts(filename):
    print("Now serving : " + filename)
    return static_file(filename, root='.')

@route('/bootstrapcss/<filename:re:.*\.css>')
def serveBootStrapCSS(filename):
    print("Now serving bootstrap CSS: " + filename)
    return static_file(filename, root='bootstrap/css')

@route('/static/<filepath:path>')
def server_static(filepath):
    print("Now serving static file: " + filepath)
    return static_file(filepath, root='.')



vocppm = 0

@route('/getdata', method='GET')
def getdata():
    global vocppm
    global op_q
    # RH, T = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 23)
    # return dict
    # dummyT = dummyT + 1
    # print repr(dummyT)
    # if dummyT >= 30:
    #     dummyT = 10
    # print("getdata")
    if not op_q.empty():
        newvocppm = op_q.get(block=False)
        if newvocppm != 0:
            vocppm=newvocppm
        print("getdata is returning: " + vocppm)
    # print("return from getdata")
    return {"RH": 0, "T": vocppm}




@route('/sendStuffToBottle', method='POST')
def do_login():
    username = request.forms.get('username')
    password = request.forms.get('password')
    print ("Bottle received username = " + username + " and password = " + password)
    return '''
    <html>
    <head>
        <script language="javascript" type="text/javascript">
            window.location.href = '/plot';
        </script>
    </html>
    '''
def read3300SerialDataDaemon(output_q, serial_port):
    print("Attempting to start Serial Daemon on " + repr(serial_port))

    # port = "COM7"
    # port = "/dev/ttyUSB0"

    ser = serial.Serial(serial_port, 9600, timeout=0)
    print("Opening " + ser.name)  # check which port was really used

    exit_daemon = False
    rxstr = ""
    O2conc = 0.0
    while not exit_daemon:
        data = ser.read(1)
        # print "Got:" + data
        if (data == '\n') | (data == '\r'):
            O2conc = parseParamagString(rxstr)
            print (O2conc)
            output_q.put(O2conc)
            rxstr = ""
        else:
            rxstr = rxstr + data
    ser.close()  # close port
    print("Exiting read3300SerialDataDaemon")

def parseParamagString(newline):
    fred = newline.split(' ')
    return fred[0]



def exit_on_keypress():
    # char = sys.stdin.read(1)
    # if char == '\n':
    #     print("Exiting !")

    # http://stackoverflow.com/questions/7255463/exit-while-loop-by-user-hitting-enter-key
    i = 0
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print ("I'm doing stuff. Press Enter to stop me!")
        print (i)
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            # line = raw_input()
            break
        i += 1

prevVal = 0.0
op_q = Queue(maxsize=5)

# main() function
def main():
    print("starting 3300 Server...")
    # create parser
    parser = argparse.ArgumentParser(description="Paramag serial server")
    parser.add_argument('--ip', dest='ipAddr', required=False)
    parser.add_argument('--port', dest='portNum', required=False)
    parser.add_argument('--serport', dest='SerPort', required=False)
    # parse args
    args = parser.parse_args()


    if(1):
        p = Process(target=read3300SerialDataDaemon, args=(op_q, args.SerPort))
        p.start()
        run(host=args.ipAddr, port=args.portNum, debug=True)
    else:
        p = Process(target=read3300SerialDataDaemon, args=(op_q, "/dev/ttyUSB1"))
        p.start()
        run(host='192.168.240.2', port=8080, debug=False)


    print("Exited bottle server")


# call main
if __name__ == '__main__':
    main()