import os
from PyQt5.QtWidgets import (
   QApplication, QWidget,
   QFileDialog, # Диалог открытия файлов (и папок)
   QLabel, QPushButton, QListWidget,
   QHBoxLayout, QVBoxLayout
)
from PyQt5.QtCore import * # нужна константа Qt.KeepAspectRatio для изменения размеров с сохранением пропорций
from PyQt5.QtGui import QPixmap, QImage # оптимизированная для показа на экране картинка
 
from PIL import Image, ImageFilter, ImageEnhance
from random import randint

class ImageProcessor(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.resize(700, 500)
        self.setWindowTitle('Easy Editor')
        self.image = None
        self.dir = None
        self.filename = None
        self.save_dir = "Modified/"
        self.pixmapimage = None
        self.original = True
    
    def event(self, e):
        if e.type() == QEvent.KeyPress:
            if e.key() == 88:
                self.saveImage()
        #ЭТО РАБОТА С ЗАКРЫТИЕМ ОКНА И НАЖАТИЕМ МЫШКИ
        # elif e.type() == QEvent.Close:
        #     print("Окно закрыто")
        # elif e.type() == QEvent.MouseButtonPress:
        #     print ("Щелчок мышью. Координаты:", e.x(), e.y())
        return QWidget.event(self, e) # Отправляем дальше

    def loadImage(self, dir, filename):
        ''' при загрузке запоминаем путь и имя файла '''
        self.dir = dir
        self.filename = filename
        image_path = os.path.join(dir, filename)
        self.image = Image.open(image_path)
    
    def do_bw(self):
        self.image = self.image.convert("L")
        image_path = os.path.join(self.dir, self.save_dir, self.filename)
        self.showImage(image_path)
    
    def do_left(self):
        self.image = self.image.transpose(Image.ROTATE_90)
        image_path = os.path.join(self.dir, self.save_dir, self.filename)
        self.showImage(image_path)
    
    def do_right(self):
        self.image = self.image.transpose(Image.ROTATE_270)
        image_path = os.path.join(self.dir, self.save_dir, self.filename)
        self.showImage(image_path)
    
    def do_flip(self):
        self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
        image_path = os.path.join(self.dir, self.save_dir, self.filename)
        self.showImage(image_path)
    
    def do_sharp(self):
        self.image = ImageEnhance.Contrast(self.image)
        self.image = self.image.enhance(1.5)
        image_path = os.path.join(self.dir, self.save_dir, self.filename)
        self.showImage(image_path)    

    def saveImage(self):
        if not(self.original):
            ''' сохраняет копию файла в подпапке '''
            path = os.path.join(self.dir, self.save_dir)
            if not(os.path.exists(path) or os.path.isdir(path)):
                os.mkdir(path)
            image_path = os.path.join(path, self.filename)
            if os.path.exists(image_path):
                filename = changedFileName(self.filename)
                image_path = os.path.join(path, filename)
            self.pixmapimage.save(image_path)
        else:
            print("Оригинал сохранить нельзя!!!")
    
    def showImage(self, path = None):
        lb_image.hide()
        if self.image != None:
            self.image = self.image.convert("RGBA")
            data = self.image.tobytes("raw", "RGBA")
            qim = QImage(data, self.image.size[0], self.image.size[1], QImage.Format_RGBA8888)
            self.pixmapimage = QPixmap(qim)
            self.original = False
        else:
            self.original = True
            self.pixmapimage = QPixmap(path)
        w, h = lb_image.width(), lb_image.height()
        self.pixmapimage = self.pixmapimage.scaled(w, h, Qt.KeepAspectRatio)
        lb_image.setPixmap(self.pixmapimage)
        lb_image.show()

app = QApplication([])

workimage = ImageProcessor() #текущая рабочая картинка для работы

lb_image = QLabel("Картинка")
btn_dir = QPushButton("Папка")
lw_files = QListWidget()
 
btn_left = QPushButton("Лево")
btn_right = QPushButton("Право")
btn_flip = QPushButton("Зеркало")
btn_sharp = QPushButton("Резкость")
btn_bw = QPushButton("Ч/Б")
btn_save = QPushButton("сохранить")
 
row = QHBoxLayout()          # Основная строка
col1 = QVBoxLayout()         # делится на два столбца
col2 = QVBoxLayout()
col1.addWidget(btn_dir)      # в первом - кнопка выбора директории
col1.addWidget(lw_files)     # и список файлов
col2.addWidget(lb_image, 95) # вo втором - картинка
row_tools = QHBoxLayout()    # и строка кнопок
row_tools.addWidget(btn_left)
row_tools.addWidget(btn_right)
row_tools.addWidget(btn_flip)
row_tools.addWidget(btn_sharp)
row_tools.addWidget(btn_bw)
row_tools.addWidget(btn_save)
col2.addLayout(row_tools)
 
row.addLayout(col1, 20)
row.addLayout(col2, 80)

workimage.setLayout(row)

workdir = ''

def filter(files, extensions):
   result = []
   for filename in files:
       for ext in extensions:
           if filename.endswith(ext):
               result.append(filename)
   return result

def chooseWorkdir():
   global workdir
   workdir = QFileDialog.getExistingDirectory()

def showFilenamesList():
   extensions = ['.jpg','.jpeg', '.png', '.gif', '.bmp']
   chooseWorkdir()
   filenames = filter(os.listdir(workdir), extensions)
 
   lw_files.clear()
   for filename in filenames:
       lw_files.addItem(filename)
 
btn_dir.clicked.connect(showFilenamesList)

def changedFileName(filename):
    if filename:
        splited = filename.split('.')
        splited[0] += '(' + str(randint(1,100)) + ')'
        newName = '.'.join(splited)
        return newName
    return filename

def showChosenImage():
   if lw_files.currentRow() >= 0:
       filename = lw_files.currentItem().text()
       workimage.loadImage(workdir, filename)
       image_path = os.path.join(workimage.dir, workimage.filename)
       workimage.showImage(image_path)
 
lw_files.currentRowChanged.connect(showChosenImage)
 
btn_bw.clicked.connect(workimage.do_bw)
btn_left.clicked.connect(workimage.do_left)
btn_right.clicked.connect(workimage.do_right)
btn_flip.clicked.connect(workimage.do_flip)
btn_sharp.clicked.connect(workimage.do_sharp)

btn_save.clicked.connect(workimage.saveImage)

workimage.show()
app.exec()
