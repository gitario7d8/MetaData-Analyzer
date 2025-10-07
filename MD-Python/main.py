import sys
print(sys.executable)

import customtkinter as custom_tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ExifTags
import os
from datetime import datetime


custom_tk.set_appearance_mode("dark")
custom_tk.set_default_color_theme("blue")

app = custom_tk.CTk()
app.title("MetaReveal Lite - Image Analyzer")
app.geometry("850x700")

current_img = None

label_image = None
textbox_result = None

def analyze_file():
    global current_img, label_image, textbox_result
    p = entry_file_path.get()
    if not os.path.exists(p):
        messagebox.showerror("Error", "File does not exist!")
        return
    
    ext = os.path.splitext(p)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png"]:
        messagebox.showerror("Error", "Only image files are supported!")
        return
    
    res = ""
try:
    img = Image.open(p)
    img.thumbnail((250,250))
    current_img = ImageTk.PhotoImage(img)
    exif = img._getexif()
    if exif:
        gps = None
        gps_tags = {}
        for t, v in exif.items():
            tag = ExifTags.TAGS.get(t, t)
            if tag == "GPSInfo":
                gps = v
            else:
                res += str(tag) + ": " + str(v) + "\n"
        if gps:
            for key in gps.keys():
                gps_tags[ExifTags.GPSTAGS.get(key, key)] = gps[key]
            if 'GPSLatitude' in gps_tags and 'GPSLongitude' in gps_tags:
                
                lat = gps_tags['GPSLatitude']
                lon = gps_tags['GPSLongitude']
                ref1 = gps_tags.get('GPSLatitudeRef', 'N')
                ref2 = gps_tags.get('GPSLongitudeRef', 'E')


                def convert_gps(coord, ref):
                    decimal = coord[0][0]/coord[0][1] + (coord[1][0]/coord[1][1])/60 + (coord[2][0]/coord[2][1])/3600
                    if ref in ['S', 'W']:
                        decimal = -decimal
                    return decimal


                d = convert_gps(lat, ref1)
                d2 = convert_gps(lon, ref2)
                res += f"GPS Latitude: {d}\nGPS Longitude: {d2}\nGoogle Maps: https://www.google.com/maps?q={d},{d2}\n"
        else:
            res += "No GPS metadata found.\n"
    else:
        res = "No EXIF metadata found."
except Exception as e:
    res = "Error reading metadata: " + str(e)
    current_img = None

try:
    s = os.stat(p)
  
    c = datetime.fromtimestamp(getattr(s, 'st_birthtime', s.st_ctime))
    m = datetime.fromtimestamp(s.st_mtime)
    res += f"\n--- FILE INFO ---\nCreated: {c}\nModified: {m}\n"
except Exception:
    pass

def update_textbox(text):
    textbox_result.configure(state="normal")
    textbox_result.delete("1.0", "end")
    textbox_result.insert("1.0", text)
    textbox_result.configure(state="disabled")

def display_image(img_obj):
    global current_img
    if img_obj:
        img_obj.thumbnail((250,250))
        current_img = ImageTk.PhotoImage(img_obj)
        label_image.configure(image=current_img)
    else:
        label_image.configure(image=None)





def open_file():
    f = filedialog.askopenfilename(filetypes=[("Images","*.jpg *.jpeg *.png")])
    if f:
        entry_file_path.configure(state="normal")
        entry_file_path.delete(0,"end")
        entry_file_path.insert(0,f)
        entry_file_path.configure(state="readonly")
        textbox_result.configure(state="normal")
        textbox_result.delete("1.0","end")
        textbox_result.configure(state="disabled")
        label_image.configure(image=None)

def save_file():
    data = textbox_result.get("1.0","end").strip()
    if not data:
        messagebox.showinfo("Info","No data to save")
        return
    f = filedialog.asksaveasfilename(defaultextension=".txt",filetypes=[("Text files","*.txt")])
    if f:
        try:
            with open(f,"w",encoding="utf-8") as x:
                x.write(data)
            messagebox.showinfo("Saved",f"Saved to {f}")
        except Exception as e:
            messagebox.showerror("Error",str(e))

frame = custom_tk.CTkFrame(app)
frame.pack(pady=15, padx=15, fill="both", expand=True)

label_title = custom_tk.CTkLabel(frame, text="MetaReveal Lite - Image Analyzer", font=("Arial", 20, "bold"))
label_title.pack(pady=10)

btn_browse = custom_tk.CTkButton(frame, text="Choose File", command=open_file)
btn_browse.pack(pady=10)

entry_file_path = custom_tk.CTkEntry(frame, placeholder_text="Selected file path will appear here", width=600)
entry_file_path.configure(state="readonly")
entry_file_path.pack(pady=5)

btn_analyze = custom_tk.CTkButton(frame, text="Analyze Metadata", command=analyze_file)
btn_analyze.pack(pady=10)

btn_save = custom_tk.CTkButton(frame, text="Save Report", command=save_file)
btn_save.pack(pady=5)

label_image = custom_tk.CTkLabel(frame)
label_image.pack(pady=10)

textbox_result = custom_tk.CTkTextbox(frame, width=800, height=300)
textbox_result.configure(state="disabled")
textbox_result.pack(pady=10)

app.mainloop()
