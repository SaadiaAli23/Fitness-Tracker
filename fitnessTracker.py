from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
from PyQt5.QtCore import *
from PyQt5.QtSql import *

import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from sys import exit

class FitnessT(QWidget):
    def __init__(self): 
        super().__init__()

        self.setWindowTitle("Fitness Tracker")
        self.resize(1100, 640)
        self.FitUI() 
        self.buttons() 


    def FitUI(self):


        self.date_w = QCalendarWidget()
        font = QFont("Arial",8)
        self.date_w.setSelectedDate(QDate.currentDate())
        self.date_w.setFont(font)


        self.weight = QSpinBox()
        self.weight.setRange(1,500)
        self.weight.setSuffix(" kg")

        
        self.duration = QLineEdit()
        self.duration.setPlaceholderText("Enter duration walked/light jogged (hours)")


        self.calculate = QPushButton("Calculate cals")
        self.add = QPushButton("Add")
        self.delete = QPushButton("Delete")
        self.clear = QPushButton("Clear")
        self.plot = QPushButton("Plot Graph")

        self.chart = QTableWidget()
        self.chart.setColumnCount(4)
        self.chart.setHorizontalHeaderLabels(["Entry #", "Date", "Calories", "Duration"])
        self.chHeader = self.chart.horizontalHeader()
        self.chHeader.setSectionResizeMode(QHeaderView.Stretch)


        self.shape = plt.figure()
        self.blank = FigureCanvas(self.shape)

        self.layout_horizontal = QHBoxLayout()
        self.col1 = QVBoxLayout()
        self.col2 = QVBoxLayout()

        self.row1 = QHBoxLayout()
        self.form = QFormLayout()
        self.row3 = QHBoxLayout()
        self.row4 = QHBoxLayout()
        self.row5 = QHBoxLayout()

        self.row1.addWidget(QLabel("Date:"))
        self.row1.addWidget(self.date_w)

        self.form.addRow("Weight (kg): ", self.weight)
        self.form.addRow("Duration (hrs): ", self.duration)

        self.row4.addWidget(self.calculate)

        self.calories_res = QLabel("Calories Burned: 0")
        self.row4.addWidget(self.calories_res)

        self.row5.addWidget(self.add)
        self.row5.addWidget(self.delete)


        self.col1.addLayout(self.row1)   
        self.col1.addLayout(self.form) 
        self.col1.addLayout(self.row3) 
        self.col1.addLayout(self.row4)
        self.col1.addLayout(self.row5)
       
        self.col1.addLayout(self.row5)

        self.col2.addWidget(self.blank)
        self.col2.addWidget(self.plot)
        self.col2.addWidget(self.chart)
        self.col2.addWidget(self.clear)


        self.layout_horizontal.addLayout(self.col1, 35) #add col1 to main layout
        self.layout_horizontal.addLayout(self.col2, 65)
        self.setLayout(self.layout_horizontal)

        self.get_data()


    def buttons(self):
        self.add.clicked.connect(self.create_log)
        self.calculate.clicked.connect(self.calculate_cals)
        self.delete.clicked.connect(self.delete_log)
        self.plot.clicked.connect(self.display_graph)
        self.clear.clicked.connect(self.clear_all)

    def get_data(self):
        query = QSqlQuery("SELECT * FROM Fitness_tracker ORDER BY Date DESC")
        self.chart.setRowCount(0)
        while query.next():
            row = self.chart.rowCount()
            Entry_num = query.value(0)
            Date = query.value(1)
            Calories = query.value(2)
            Duration = query.value(3)

            self.chart.insertRow(row)
            self.chart.setItem(row, 0, QTableWidgetItem(str(Entry_num)))
            self.chart.setItem(row, 1, QTableWidgetItem(Date))
            self.chart.setItem(row, 2, QTableWidgetItem(str(Calories)))
            self.chart.setItem(row, 3, QTableWidgetItem(str(Duration)))
         
    
    def create_log(self):
        Date = self.date_w.selectedDate().toString("yyyy-MM-dd")
        Calories = self.calories_res.text().replace("Calories Burned: ", "") # do we need the replace and ""
        Duration = self.duration.text()

        query = QSqlQuery("""
                            INSERT INTO Fitness_tracker (Date, Calories, Duration)
                            VALUES (?,?,?)
                            """)
        
        query.addBindValue(Date)
        query.addBindValue(Calories)
        query.addBindValue(Duration)
        query.exec_()
        
        self.calories_res.setText("Calories Burned: 0")
        self.date_w.setSelectedDate(QDate.currentDate())

        self.get_data()

    def delete_log(self):
        row = self.chart.currentRow()

        if row < 0:
            QMessageBox.warning(self,"Warning", "Choose a valid row to remove")
            return

        entry = int(self.chart.item(row,0).text())
        
        query = QSqlQuery()
        query.prepare("DELETE FROM Fitness_tracker WHERE Entry_num = ?")
        query.addBindValue(entry)

    
        query.exec_()

        self.get_data()

        
    def display_graph(self):
        calories = []
        dates = []

        query = QSqlQuery("SELECT Calories, Date FROM Fitness_tracker ORDER BY DATE")
        while query.next():
            cals = query.value(0)
            date = query.value(1)
            calories.append(cals)
            dates.append(date)

        self.shape.clear()

        plt.style.use("ggplot")
        bar_g = self.shape.add_subplot()
        bar_g.bar(dates,calories, 0.5, color='lightblue')

        if len(dates) == 1:
            bar_g.set_xlim(-1,1)

        bar_g.set_title('Calories Burned Over Time', fontweight='bold')
        bar_g.set_xlabel('Date')
        bar_g.set_ylabel('Calories')


        self.blank.draw()

    def calculate_cals(self):
        try :
            weight_input = self.weight.value()
            duration_input = float(self.duration.text())
            
            calories_burned = 6 * weight_input * duration_input
            calories_str = str(calories_burned)
            self.calories_res.setText("Calories Burned: " + calories_str) #display somewhere else not description 
        except ValueError:
            self.calories_res.setText("Invalid Request")
            


    def clear_all(self):
        self.calories_res.setText("Calories Burned: 0")
        self.duration.clear()
        self.shape.clear()
        self.blank.draw()
        self.weight.clear()




    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName("Fitness_tracker.db")

    if not db.open():
            print("Failed to open the database")
 

query = QSqlQuery()
query.exec("""
            CREATE TABLE IF NOT EXISTS Fitness_tracker (
                Entry_num INTEGER PRIMARY KEY AUTOINCREMENT, 
                Date TEXT NOT NULL,
                Calories INTEGER NOT NULL,
                Duration REAL NOT NULL
           )
           """)

if __name__ == "__main__": 
    app = QApplication(sys.argv)
    window = FitnessT()
    window.setStyleSheet("""
            QWidget {
                background-color: #C4DFE6;             
            }
            QPushButton {
                background-color: #66A5AD; 
                color: white;
                border-radius: 10px;
                padding: 10px 10px;                    
            }
            QPushButton:hover {
                background-color: #457a81           
            }                         
            QTableWidget {
                border: 2.5px solid #66A5AD;    
            }
            QCalendarWidget QAbstractItemView{
                border: 1.5px solid #66A5AD;
                background-color: #FFFFFF;    
                         
            }
""")
    window.show()
    app.exec()
