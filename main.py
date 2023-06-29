import tkinter as tk
import pyautogui
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageGrab
from screeninfo import get_monitors
import time
from moviepy.editor import VideoFileClip


class ScreenRecorder:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.is_recording = False
        self.is_paused = False
        self.playBtn = ImageTk.PhotoImage(Image.open("play.png").resize((70, 70)))
        self.pauseBtn = ImageTk.PhotoImage(Image.open("pause.png").resize((70, 70)))
        self.stopBtn = ImageTk.PhotoImage(Image.open("stop.png").resize((70, 70)))
        self.closeBtn = ImageTk.PhotoImage(Image.open("close.png").resize((20, 20)))
        self.Close = tk.Button(self.master, image= self.closeBtn, command= self.close_window)
        self.Close.pack(anchor="ne")
        self.Time = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        self.choose_monitor()
        # self.create_recorder()

    def close_window(self):
        self.master.destroy()
    
    def choose_monitor(self):
        monitorsInfo = get_monitors()
        self.monitorList = [[monitor.width, monitor.height, monitor.name.replace("\\","").replace(".", "")] for monitor in monitorsInfo]
        self.monitorBtn = []
        for i in range(len(self.monitorList)):
            self.monitorBtn.append(tk.Button(self.master, text = f"螢幕{i+1}", font=("Arial", 20), command= lambda idx=i: self.create_recorder(idx)))
            self.monitorBtn[i].pack(side= "left", padx= 5)

    def create_recorder(self, idx):
        self.whichImg = idx + 1
        self.screenWidth = self.monitorList[idx][0]
        self.screenHeight = self.monitorList[idx][1] #這決定錄製影片的尺寸
        if idx == 0:
            self.imgStartX = 0
            self.imgStartY = 0
            self.imgEndX = self.monitorList[idx][0]
            self.imgEndY = self.monitorList[idx][1]
           
        else:
            self.imgStartX = self.monitorList[idx][0]
            self.imgStartY = 0
            self.imgEndX = self.monitorList[idx-1][0] + self.monitorList[idx][0]
            self.imgEndY = self.monitorList[idx][1]
        self.master.geometry(f"150x100+{self.imgEndX-300}+{self.imgEndY - 200}")

        for i in range(len(self.monitorBtn)):
            self.monitorBtn[i].pack_forget()
        self.record_button = tk.Button(self.master, text="開始錄製", image= self.playBtn, command=self.toggle_recording)
        self.record_button.pack(side="left")

        self.stop_button = tk.Button(self.master, text="停止錄製", image= self.stopBtn,command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(side= "right")

        # 載入自訂滑鼠指標圖片
        self.cursor_image = cv2.imread("cursor.jpg")
        self.cursor_image = cv2.resize(self.cursor_image, (100, 100))

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        elif self.is_paused:
            self.resume_recording()
        else:
            self.pause_recording()

    def start_recording(self):
        self.is_recording = True
        self.record_button.config(text="暫停錄製", image= self.pauseBtn)
        self.stop_button.config(state=tk.NORMAL)
        self.output = cv2.VideoWriter(f'./video/{self.Time}.mp4', cv2.VideoWriter_fourcc(*'MP4V'), 8.0, (self.screenWidth, self.screenHeight))
        # self.output = cv2.VideoWriter(f'./video/{time.strftime("%Y%m%d-%H%M%S", time.localtime())}.mp4', cv2.VideoWriter_fourcc(*'MP4V'), 8.0, (3840, 1080))
        self.record_screen()

    def stop_recording(self):
        self.master.geometry(f"200x100+{x-300}+{y-200}")
        self.is_recording = False
        self.record_button.config(text="開始錄製", image= self.playBtn)
        self.stop_button.config(state=tk.DISABLED)
        self.output.release()
        cv2.destroyAllWindows()
        self.record_button.pack_forget()
        self.stop_button.pack_forget()
        self.choose_monitor()

    def pause_recording(self):
        self.is_paused = True
        self.record_button.config(text="繼續錄製", image= self.playBtn)

    def resume_recording(self):
        self.is_paused = False
        self.record_button.config(text="暫停錄製", image= self.pauseBtn)

    def record_screen(self):
        while self.is_recording:
            if not self.is_paused:
                img = ImageGrab.grab(all_screens= True)
                imgX, imgY = img.size
                frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                # 取得滑鼠位置
                x, y = pyautogui.position()
                # 計算鼠標圖片的顯示範圍
                cursor_height, cursor_width, _ = self.cursor_image.shape
                x_start = max(0, x)
                y_start = max(0, y)
                x_end = min(imgX, x + cursor_width)
                y_end = min(imgY, y + cursor_height)

                # print(x_start, y_start, x_end, y_end)

                # 取得鼠標圖片在畫面上的位置

                cursor_x_start = x_start - x
                cursor_y_start = y_start - y
                cursor_x_end = cursor_x_start + (x_end - x_start)
                cursor_y_end = cursor_y_start + (y_end - y_start)

                # 裁剪鼠標圖片，僅保留顯示範圍內的部分
                cursor_image_cropped = self.cursor_image[cursor_y_start:cursor_y_end, cursor_x_start:cursor_x_end]
                
                # 更新畫面上的鼠標圖片
                frame[y_start:y_end, x_start:x_end] = cursor_image_cropped
                tmp = cv2.cvtColor(np.array(Image.fromarray(frame)), cv2.COLOR_RGB2BGR)
                result = tmp[self.imgStartY:self.imgEndY, self.imgStartX: self.imgEndX]
                result = cv2.cvtColor(np.array(result), cv2.COLOR_RGB2BGR)
                self.output.write(result)
            self.master.update()

    def video_speed(self):
        clip = VideoFileClip(f"./video/{self.Time}.mp4")
        slowClip = clip.fx(VideoFileClip.fx, lambda x: x.speedx(1))
        slowClip.write_videofile(f"./video/{self.Time}.mp4")



root = tk.Tk()
root.title("螢幕錄製程式")
root.iconbitmap("recorder.ico")
root.attributes("-topmost", 1)
root.overrideredirect(True)
x, y = pyautogui.size()
root.geometry(f"200x100+{x-300}+{y-200}")
app = ScreenRecorder(root)

root.mainloop()
