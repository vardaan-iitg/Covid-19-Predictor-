import os
import sys
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets, QtWebChannel
from jinja2 import Template
import pyttsx3
import sys
import duplicate
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, QCoreApplication
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QMessageBox, QWidget, QApplication, QTableWidget, QTableWidgetItem, QPushButton

import time
import threading


class Element(QtCore.QObject):
    def __init__(self, name, parent=None):
        super(Element, self).__init__(parent)
        self._name = name

    @property
    def name(self):
        return self._name

    def script(self):
        raise NotImplementedError


class FormObject(Element):
    numbersChanged = QtCore.pyqtSignal(str, str, str)

    def script(self):
        _script = r"""
        var btn = document.getElementById('sub1');
        var btn2=document.getElementById('none');
        btn.addEventListener("click", function(event){
            var number1 = document.getElementById('num1').value;
            var z=document.getElementById('me2').value;

            var sk=document.getElementById('num1').value;
            localStorage.setItem("firstname",sk);
            var number2 = document.getElementById('num2');
             var x=number2.value
            {{name}}.update(number1,x,z);
        });
        btn2.addEventListener("click", function(event){
            var number1 = document.getElementById('num1').value;
            var z=document.getElementById('me2').value;
            var number2 = document.getElementById('num2');
             var x=number2.value
            {{name}}.update2(number1,x,z);
        });
        
        """
        return Template(_script).render(name=self.name)

    @QtCore.pyqtSlot(str, str, str)
    def update(self, number1, number2, n3):
        self.numbersChanged.emit(number1, number2, n3)

    @QtCore.pyqtSlot(str, str, str)
    def update2(self, number1, number2, n3):
        #self.numbersChanged.emit(number1, number2, n3)
        #self.hide()
        self.s = duplicate.App()
        self.s.show()


class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    def __init__(self, *args, **kwargs):
        super(WebEnginePage, self).__init__(*args, **kwargs)
        self.loadFinished.connect(self.onLoadFinished)
        self._objects = []

    def add_object(self, obj):
        self._objects.append(obj)

    @QtCore.pyqtSlot(bool)
    def onLoadFinished(self, ok):
        if ok:
            self.load_qwebchannel()
            self.load_objects()

    def load_qwebchannel(self):
        file = QtCore.QFile(":/qtwebchannel/qwebchannel.js")
        if file.open(QtCore.QIODevice.ReadOnly):
            content = file.readAll()
            file.close()
            self.runJavaScript(content.data().decode())
        if self.webChannel() is None:
            channel = QtWebChannel.QWebChannel(self)
            self.setWebChannel(channel)

    def load_objects(self):
        if self.webChannel() is not None:
            objects = {obj.name: obj for obj in self._objects}
            self.webChannel().registerObjects(objects)
            _script = r"""
            {% for obj in objects %}
            var {{obj}};
            {% endfor %}
            new QWebChannel(qt.webChannelTransport, function (channel) {
            {% for obj in objects %}
                {{obj}} = channel.objects.{{obj}};
            {% endfor %}
            }); 
            """
            self.runJavaScript(Template(_script).render(objects=objects.keys()))
            for obj in self._objects:
                if isinstance(obj, Element):
                    self.runJavaScript(obj.script())


class WebPage(QtWebEngineWidgets.QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)

        page = WebEnginePage(self)
        self.setPage(page)
        self.setFixedWidth(910)
        self.setFixedHeight(700)
        self.setGeometry(50,50,910,700)
        formobject = FormObject("formobject", self)
        formobject.numbersChanged.connect(self.on_numbersChanged)
        page.add_object(formobject)

        filepath = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "form.html")
        )
        self.load(QtCore.QUrl.fromLocalFile(filepath))

    @QtCore.pyqtSlot(str, str,str)
    def on_numbersChanged(self, number1, number2, n3):
        print(n3)
        pr = "Thankyou for submitting your response" + number1
        if number1 != "":
            if number2 != "":
                import sqlite3
                import logging
                # conn=sqlite3.connect('database_final.db')
                conn = sqlite3.connect('database.db')
                #conn.execute("CREATE TABLE Users(Id integer primary key autoincrement, Name TEXT,rating TEXT,suggestions TEXT)")
                conn.execute("INSERT INTO Users(Name,rating,suggestions)values(?,?,?)",(number1,number2,n3))
                conn.commit()
                #logging.info('record created')
                #print(conn.execute('select * from users').fetchall())
                conn.close()
        if number1 != "":
            x = pyttsx3.init()
            # x.setProperty('rate', 150)
            # x.setProperty('volume', 100)
            x.say(pr)
            x.runAndWait()
            exit()
        else:
            x = pyttsx3.init()
            # x.setProperty('rate', 150)
            # x.setProperty('volume', 100)
            x.say("Please fill our feedback form")
            x.runAndWait()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    web = WebPage()


    # GUI = ChatInterface()
    # GUI.show()
    def fun():
        web.destroy()


    def fun2():
        x = pyttsx3.init()
        x.say("hello")
        x.runAndWait()


    web.show()
    # MainWindow.show()
    # app.aboutToQuit.connect(fun2)
    sys.exit(app.exec_())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    web = WebPage()
    web.show()
    sys.exit(app.exec_())
