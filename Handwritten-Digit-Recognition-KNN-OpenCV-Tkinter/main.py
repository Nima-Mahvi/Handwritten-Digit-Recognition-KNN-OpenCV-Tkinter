import cv2
import numpy as np
import pandas as pd
import tkinter
from tkinter import *
from tkinter import filedialog , messagebox
from PIL import ImageGrab , Image , ImageDraw , ImageTk
import os

class Paint(object):

    DEFAULT_PEN_SIZE = 23.0
    DEFAULT_COLOR = 'white'
    messagebox.showinfo("Guide","Hi!  Please draw a one-digit number from 0 to 9.\n If you did not write the number correctly, you can try again by pressing the (Clear) button.\n After finishing writing, click on the button to (Recognition of the written number).")
        
    def __init__(self):
        
        self.root = Tk()
        self.root.title("Recognition of handwriting numbers")
        
        self.pen_button = Button(self.root, text='Pen', command=self.use_pen)
        self.pen_button.grid(row=1, column=0)

        self.clear_all_button = Button(self.root, text='Clear', command=self.clear_all)
        self.clear_all_button.grid(row=1, column=1)
        
        self.save_button = Button(self.root, text='Recognition of the written number', command=self.Recognition)
        self.save_button.grid(row=1, column=2)
        
        self.choose_size_button = Scale(self.root, from_=23, to=23)
        self.choose_size_button.grid(row=2, column=1)

        self.c = Canvas(self.root, bg='black', width=400, height=400)
        self.c.grid(row=2, columnspan=5)

        self.setup()
        self.root.mainloop()

    def setup(self):
        self.old_x = None
        self.old_y = None
        self.line_width = self.choose_size_button.get()
        self.color = self.DEFAULT_COLOR
        self.eraser_on = False
        self.active_button = self.pen_button
        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)

    def use_pen(self):
        self.activate_button(self.pen_button)
        
    def clear_all(self):
        self.c.delete("all")
        self.setup()
        
    
    def Recognition(self):
        global cells2 , test_cells_flat , targets
        current_directory = os.getcwd()

        try:
            self.root.update()
            x = self.root.winfo_rootx() + self.c.winfo_x()
            y = self.root.winfo_rooty() + self.c.winfo_y()
            x1 = x + self.c.winfo_width()
            y1 = y + self.c.winfo_height()

            image = ImageGrab.grab(bbox=(x, y, x1, y1))

            image = image.resize((20, 20), Image.BICUBIC)

            default_file_path = os.path.join(current_directory, "image.png")

            image.save(default_file_path, "PNG")
            
            # digits=cv2.imread("digits.png",cv2.IMREAD_GRAYSCALE)
            test_digits=cv2.imread("image.png",cv2.IMREAD_GRAYSCALE)
            test_digits[0:1,:]=0
            test_digits[19:,:]=0
            test_digits[:,0:1]=0
            test_digits[:,19:]=0
            
            # rows=np.vsplit(digits,50)
            
            ######################################### train and test data
            # cells=[]
            # cells2=[]
            # for row in rows :
            #     row_cells=np.hsplit(row,100)
            #     for cell in row_cells:
            #         cells.append(cell)
            #         #all in one column 
            #         cells2.append(cell.flatten())
            
            # cells2=np.array(cells2,dtype=np.float32)
            # np.savetxt("train_data.csv", cells2,delimiter=",",fmt="%f")
            
            cells2=np.loadtxt("train_data.csv",delimiter=",")
            cells2=np.array(cells2,dtype=np.float32)
            
            #test section
            test_cells_flat=test_digits.flatten()
            test_cells_flat=np.array(test_cells_flat,dtype=np.float32)
            test_cells_flat=test_cells_flat.reshape(1,-1)
            
            
            ######################################## targets
            # n=np.arange(10)
            # targets=np.repeat(n,500)
            # np.savetxt("train_targets.csv", targets,delimiter=",",fmt="%f")
            
            targets=np.loadtxt("train_targets.csv",delimiter=",")
            targets=np.array(targets,dtype=np.float32)
            
            ######################################## KNN training
            
            knn=cv2.ml.KNearest_create()
            knn.train(cells2,cv2.ml.ROW_SAMPLE,targets)
            
            ####################################### Evaluation
            
            ret,result,neighbours,dist=knn.findNearest(test_cells_flat,k=5)
            str_result=str(int(result[0][0]))
            
            confirm=messagebox.askyesnocancel("Result",f"Detected number:   {str_result}\n Did I recognize this number correctly?")
            if confirm:
                cells2=np.vstack([cells2,test_cells_flat])
                cells2=np.array(cells2,dtype=np.float32)
                np.savetxt("train_data.csv", cells2,delimiter=",",fmt="%f")
                
                result=result.ravel()
                targets=np.hstack([targets,result])
                targets=np.array(targets,dtype=np.float32)
                np.savetxt("train_targets.csv", targets,delimiter=",",fmt="%f")
                
                messagebox.showinfo("Good news!","Good! :) \n This number is saved for better handwriting recognition in the future.")
                self.clear_all()
                
            if not confirm:
                enter_number=tkinter.Toplevel(self.root)
                enter_number.title('what was the correct number? :(')
                enter_number.geometry('470x200')
                
                lbl_enter_number=tkinter.Label(enter_number,text='Sorry for my mistake! \n What number did you write? \n please type it and click OK. \n')
                lbl_enter_number.pack()
                
                user_number=tkinter.Entry(enter_number)
                user_number.pack()
                
                def ok():
                    global cells2 , test_cells_flat , targets ,btn_ok
                    
                    number=user_number.get()
                    
                    if number=='':
                        lbl_enter_number.configure(text="\n You have not type any number yet! \n \n",fg="red")
                    
                    if number:
                        
                        cells2=np.vstack([cells2,test_cells_flat])
                        cells2=np.array(cells2,dtype=np.float32)
                        np.savetxt("train_data.csv", cells2,delimiter=",",fmt="%f")
                        
                        number=[number]
                        number=np.array(number,dtype=np.float32)
                        targets=np.hstack([targets,number])
                        targets=np.array(targets,dtype=np.float32)
                        np.savetxt("train_targets.csv", targets,delimiter=",",fmt="%f")
                        
                        messagebox.showinfo("Thank you!","Thank you! \n This number will be saved for better handwriting recognition in the future.")
                        enter_number.destroy()
                        self.clear_all()
                         
                btn_ok=tkinter.Button(enter_number,text='OK' ,command=ok)
                btn_ok.pack()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error processing image data: {e}")

    def activate_button(self, some_button, eraser_mode=False):
        self.active_button.config(relief=RAISED)
        some_button.config(relief=SUNKEN)
        self.active_button = some_button
        self.eraser_on = eraser_mode

    def paint(self, event):
        self.line_width = self.choose_size_button.get()
        paint_color = 'black' if self.eraser_on else self.color
        if self.old_x and self.old_y:
            self.c.create_line(self.old_x, self.old_y, event.x, event.y,
                               width=self.line_width, fill=paint_color,
                               capstyle=ROUND, smooth=TRUE, splinesteps=36)
        self.old_x = event.x
        self.old_y = event.y

    def reset(self, event):
        self.old_x, self.old_y = None, None


if __name__ == '__main__':
    Paint()

















