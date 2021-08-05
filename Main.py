
'''
┏┓╋╋╋╋┏━┳┓
┃┣┳━┳━┫━┫┗┳━┓
┃━┫╋┃╋┣━┃┃┃╋┗┓
┗┻┻━┻━┻━┻┻┻━━┛

01101011 01101111 01101111 01110011 01101000 01100001 

This software is made for software development 3/4 all rights reserved

the purpose of this program is to 
'''



#importing the necessary libraries 
import csv
from os import SCHED_OTHER, curdir, fstatvfs
import traceback, sys
import platform
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import base64
import yfinance as yf
import time, threading

# GUI FILE
from UImain import Ui_MainWindow
import Mthreading 
import LogIn_Ui 

import SignUp_Ui 

global Kill_t #used to kill the current thread
global New_ticker # to store the ticker
global user_name #to save the username
global current_user #to store current user
global thread #for threading 
global timeframe #to store the time frame
global Short #to store the short value
global smoothing #to store the smoothing 
global fast #to store the fast value
global data_length #how many days of data

Kill_t = False
SIGNUP = False

#sets the multi threadign limit to one 
thread = threading.Timer(1,None)

#saves the name of the user pass file
filename = "data.csv" # CSV file


#this class is for handeling login gui and functions 
#input is ui paraments and args
class Login(QDialog):
    #adjustments of the class and ui
    def __init__(self, parent = None):
        QDialog.__init__(self,parent)
        #to start the ui
        self.ui =  LogIn_Ui.Ui_Form()
        self.ui.setupUi(self)
        self.show()

        ## ==> SET UI DEFINITIONS
        #UIFunctions.uiDefinitions(self)
        self.ui.Login_L.clicked.connect(self.handleLogin)
        self.ui.SignUp_L.clicked.connect(self.handleSignin)

    
    #input: self user_name user_pass current_user also ui elements such as different inputs
    # this code will use the inputs from the ui to check the user and pass 
    #output : Null or Accept()
    def handleLogin(self):
        #global functions 
        global user_name 
        global user_pass
        global current_user

        #inputs the user from the gui an d changes the form to base64 encryption 
        user_name = str(base64.b64encode(self.ui.user_l.toPlainText().encode("utf-8")))
        user_pass = []
        current_user = []

        #field validation 
        if (self.ui.user_l.toPlainText() == '' or
            self.ui.lineEdit.text() == ''):
            QtWidgets.QMessageBox.warning(self, 'Error', 'please fill all of the requirements')
            return

        #to read the csv file
        with open('data.csv', 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            #imports the data from the csv file 
            for row in csv_reader:
                user_pass.append(row)


        ### selection sort ###
        # shearches through all the elements
        for i in range(len(user_pass)):
            
            # Find the minimum element in remaining unsorted array
            min_element = i
            for j in range(i+1, len(user_pass)):
                if user_pass[min_element][0] > user_pass[j][0]:
                    min_element = j
                    
            # Swap the found minimum element with the first element        
            user_pass[i], user_pass[min_element] = user_pass[min_element], user_pass[i]
    
        ### End of selection sort ###   


        #writing the sorted user and pass to the CSV file 
        with open(filename, 'w') as csvfile:  
            # creating a csv writer object  
            csvwriter = csv.writer(csvfile)  
            # writing the data rows  
            csvwriter.writerows(user_pass) 


        #linear search to find user and pass
        for i in user_pass:
            # the first element which is the username
            if (i[0] == user_name and str(i[1]) == str(base64.b64encode(self.ui.lineEdit.text().encode("utf-8")))):
                self.accept()
                current_user = i
                return

        #display error 
        QtWidgets.QMessageBox.warning(self, 'Error', 'incorrect user or password')



    #input: self 
    #output: null
    # Will handle the transition to Sign up page    
    def handleSignin(self):
        self.cams = SignUp()
        self.cams.show()

   


#the sign up class to access the SignUp_Ui 
class SignUp(QDialog):
    
    def __init__(self, parent = None):
        QDialog.__init__(self,parent)

        self.ui = SignUp_Ui.sUi_Form()
        self.ui.setupUi(self)
        self.show()

        
        self.ui.Login_s.clicked.connect(self.handleLogin)
        self.ui.SignUp_s.clicked.connect(self.registration)

    #input: self
    # to handle transition to the login page
    def handleLogin(self):
        self.close()    


    #input: self
    # performs field checks and saves the user and password
    def registration(self):

        #field validation to check if all the blocks are filled
        if self.ui.user_s.toPlainText() == '' or self.ui.pass_s.text() == '' or self.ui.lineEdit_2.text() == '':
            QtWidgets.QMessageBox.warning(self, 'Error', 'Please Complete all of the requirements!')
            return
        #to check to see if the passwords match 
        elif self.ui.pass_s.text() != self.ui.lineEdit_2.text() :
            QtWidgets.QMessageBox.warning(self, 'Error', "The passwords don't match!")
            return        

        #to check to see if the username already exists
        with open('data.csv', 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            #linear search
            for row in csv_reader:
                if row[0]== str(base64.b64encode(self.ui.user_s.toPlainText().encode("utf-8"))):
                    QtWidgets.QMessageBox.warning(self, 'Error', "Username already exists!")
                    return

        #storign the user and the encoded password
        user_pass = [ 
            [
                base64.b64encode(self.ui.user_s.toPlainText().encode("utf-8")) , #encrypted username
                base64.b64encode(self.ui.pass_s.text().encode("utf-8")) #encrypted pasword
                ]
                ]

        #writing the user pass to the CSV file 
        with open(filename, 'a') as csvfile:  
            # creating a csv writer object  
            csvwriter = csv.writer(csvfile)  
            # writing the data rows  
            csvwriter.writerows(user_pass) 

        QtWidgets.QMessageBox.information(self, 'registration', "All Done :)")
        return



#To access the UImain.py 

class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        QMainWindow.__init__(self,parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()
        self.threadpool = QThreadPool()

        #minimizing multi threading to avoid bugs:
        self.threadpool.setMaxThreadCount(1)

        # connecting the ui to the code
        self.ui.Addin_b.clicked.connect(self.Add_To_List)
        self.ui.refresh.clicked.connect(self.kill_run)
        self.ui.pushButton.clicked.connect(self.Edit_list)


    #handeling the delete function 
    def Edit_list(self):
        global New_ticker
        global user_pass
        global current_user
        user_pass = []

        if self.ui.textEdit.toPlainText()=='':
            QtWidgets.QMessageBox.warning(self, 'Error', "Pleas enter a ticker")
            return

        del_ticker = (self.ui.textEdit.toPlainText()).upper()
        #to read the csv file
        with open('data.csv', 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            #linear search
            for row in csv_reader:
                user_pass.append(row)

        result = self.binarySearch(user_pass, 0, len(user_pass)-1, user_name) 

        if del_ticker in user_pass[result]:
            user_pass[result].remove(del_ticker)
            QtWidgets.QMessageBox.information(self, 'done', "Ticker was deleted")

        else:
            QtWidgets.QMessageBox.warning(self, 'Error', "Ticker is already not in your list")
            return



        #adding the new adjustment to the data base
        with open(filename, 'w') as csvfile:  
            # creating a csv writer object  
            csvwriter = csv.writer(csvfile)  
            # writing the data rows  
            csvwriter.writerows(user_pass) 

    # handels the threadign 
    #input New_input

    def Add_To_List(self):
        global New_ticker
        New_ticker = self.ui.New_input.toPlainText().upper() if self.ui.New_input.toPlainText() != '' else QtWidgets.QMessageBox.warning(self, 'Error', "Pleas enter a new ticker")
        self.ui.New_input.setText('Loading')
        # adjusting the thread
        worker = Mthreading.Worker(self.getting_price) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.Add_To_List_out)
        # Execute
        self.threadpool.start(worker)


    #this will kil an existing thread in order to prevent bugs and then it runs a new one
    #no input or output
    def kill_run(self):
        global thread
        if thread.is_alive() != True:
            self.running_macd()

    #this function is ran by the thread to prevent crashes it checks for the price of a ticker 
    #input (gets the global value of the ticker)
    def getting_price(self,progress_callback):
        global New_ticker
        global user_pass
        global current_user
        user_pass = []

        #to read the csv file
        with open('data.csv', 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            #linear search
            for row in csv_reader:
                user_pass.append(row)

    
        #using the yahoo finance library it gets the info
        ticker = yf.Ticker(New_ticker)

        if str(ticker.info['regularMarketPrice']) != 'None' : 
            result = self.binarySearch(user_pass, 0, len(user_pass)-1, user_name) 
            if New_ticker not in user_pass[result]:
                user_pass[result].append(New_ticker)
                current_user = user_pass[result]
            else:
                result = -2
        else:
            result = -1


        #adding the new adjustment to the data base
        with open(filename, 'w') as csvfile:  
            # creating a csv writer object  
            csvwriter = csv.writer(csvfile)  
            # writing the data rows  
            csvwriter.writerows(user_pass) 

        return result


    #out put of the thread
    def Add_To_List_out(self,s):
        if s >= 0:
            QtWidgets.QMessageBox.information(self, 'Done', "Ticker was added successfully.")
        elif s == -2:
            QtWidgets.QMessageBox.warning(self, 'Error', "The ticker already exists.")
        else:
            QtWidgets.QMessageBox.critical(self, 'Error', "Ticker was not found!")
        self.ui.New_input.clear()




    #this code will run the mac_d in the background it also turns the multi threading on
    #input null
    #out put null
    def running_macd(self):
        global timeframe #to store the time frame
        global Short #to store the short value
        global smoothing #to store the smoothing 
        global fast #to store the fast value
        global data_length
        global current_user

        Short = self.ui.short_in.toPlainText()
        smoothing = self.ui.smooth.toPlainText()
        fast = self.ui.long_in.toPlainText()

        #to find the value of the radio buttons 
        if self.ui.m5.isChecked():
            timeframe = "5m"
            data_length = '2d'
        elif self.ui.m15.isChecked():
            timeframe = "15m" 
            data_length = '2d'
        elif self.ui.m30.isChecked():
            timeframe = "30m"
            data_length = '2d'
        elif self.ui.h1.isChecked():
            timeframe = "60m"
            data_length = '7d'
        elif self.ui.d1.isChecked():
            timeframe = "1d"
            data_length = '40d'


        if Short == '' or smoothing == '' or fast == '':
            QtWidgets.QMessageBox.warning(self, 'Error', "Please fill all of the fields")
            return

        #field validation 
        try:
            Short = int(Short)
        except:
            QtWidgets.QMessageBox.critical(self, 'Error', "Please enter a number for short")
            return

        #field validation 
        try:
            smoothing = int(smoothing)
        except:
            QtWidgets.QMessageBox.critical(self, 'Error', "Please enter a number for smooth")
            return  

        #field validation                
        try:
            fast = int(fast)
        except:
            QtWidgets.QMessageBox.critical(self, 'Error', "Please enter a number for long")
            return         

        
        if current_user[2:] == []:
            QtWidgets.QMessageBox.critical(self, 'Error', "Please add tickers first")
            return

        # adjusting the thread
        worker = Mthreading.Worker(self.loading_handle) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.loading_handle_out)
        # Execute
        self.threadpool.start(worker)

    #this function will keep the code running in the background without the UI crashing
    #input (macd values in the ui)
    #output result of macd
    def loading_handle(self,progress_callback):
        global current_user
        global data_length
        global timeframe #to store the time frame
        global Short #to store the short value
        global smoothing #to store the smoothing 
        global fast #to store the fast value
        alarm_list=[]#will store the tickers that need to be alarmed
        results=[] # [ticker,price,stat]
        current_ticker = current_user[2:] #getting only the tickers
    
        for i in current_ticker:
            df = yf.download(tickers = i, period=data_length, interval=timeframe)
            #calculating short ema 26
            ShortEMA = df.Close.ewm(span=Short, adjust=False).mean()
            #calculating long ema 13
            LongEMA = df.Close.ewm(span=fast, adjust=False).mean()
            #calculating the MACD 9
            MACD = ShortEMA - LongEMA
            #calculating the signal
            signal = MACD.ewm(span=smoothing, adjust=False).mean()

            if MACD[-1] > signal[-1]:
                stat = "Long"
                if MACD[-2] < signal[-2]:
                    alarm_list.append([i,"MACD Cross Up"])
            else:
                stat = "Short"
                if MACD[-2] > signal[-2]:
                    alarm_list.append([i,"MACD Cross Down"])

            results.append([i,str(round(df['Close'][-1],4)),stat])
        print(results)
        return [results,alarm_list]

    def loading_handle_out(self,s):
        global thread
        global timeframe

        #to transfare timeframe to time in seconds
        ttime = ''
        numbers = [int(word) for word in list(timeframe) if word.isdigit()]
        for i in numbers:
            ttime += str(i)
          
        ttime = int(ttime) * 60 

        print(ttime)
        
        for i in s[1]:
            QtWidgets.QMessageBox.information(self, 'alarm', i[0] + i[1] )

        self.quickSort(s[0], 0, len(s[0])-1)
        count = 0
        for i in s[0]:
            self.ui.tableWidget.setItem(count, 0, QTableWidgetItem(i[0]))
            self.ui.tableWidget.setItem(count, 1, QTableWidgetItem(i[1]))
            self.ui.tableWidget.setItem(count, 2, QTableWidgetItem(i[2]))
            count += 1
        thread = threading.Timer(ttime, self.running_macd)
        thread.start()
        


#### for quick sorting ###

#this will sort the out put for the table
    def partition(self, arr_list, low, high):
        i = (low-1)		 # index of smaller element
        pivot = arr_list[high][0]	 # pivot

        for j in range(low, high):

            # If current element is smaller than or
            # equal to pivot
            if arr_list[j][0] <= pivot:

                # increment index of smaller element
                i = i+1
                arr_list[i], arr_list[j] = arr_list[j], arr_list[i]

        arr_list[i+1], arr_list[high] = arr_list[high], arr_list[i+1]
        return (i+1)

    def quickSort(self, arr_list, low, high):
        #will return the current list if there is only one element
        if len(arr_list) == 1:
            return arr_list

        if low < high:

            # pi is partitioning index, arr_list[p] is now
            # at right place
            pi = self.partition(arr_list, low, high)

            # Separately sort elements before
            # partition and after partition
            self.quickSort(arr_list, low, pi-1)
            self.quickSort(arr_list, pi+1, high)
########## End of quick sort ##########

#start of binarySearch 
#input array, first elements place, last element's place, what to search for
# Returns index of x in arr_list if present, else -1 
    def binarySearch (self, arr_list, l, r, x): 
        # Check base case 
        if r >= l: 

            mid = l + (r - l) // 2

            # If element is present at the middle itself 
            if arr_list[mid][0] == x: 
                return mid 
            
            # If element is smaller than mid, then it 
            # can only be present in left subarray 
            elif arr_list[mid][0] > x: 
                return self.binarySearch(arr_list, l, mid-1, x) 

            # Else the element can only be present 
            # in right subarray 
            else: 
                return self.binarySearch(arr_list, mid + 1, r, x) 

        else: 
            # Element is not present in the array 
            return -1

#end of binarysearch 



# The main loop to run the UI
if __name__ == '__main__':

    import sys
    app = QtWidgets.QApplication(sys.argv)
    login = Login()

    
    #handeling the page transition 

    if login.exec_() == QtWidgets.QDialog.Accepted:
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())

    if SIGNUP == True:
        window = SignUp()
        window.show()
        sys.exit(app.exec_())
    
