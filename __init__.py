# -*- coding: utf-8 -*-

"""
Anki Add-on: Edit Field During Review

Edit text in a field during review without opening the edit window

Copyright: (c) 2019-2020 Nickolay Nonard <kelciour@gmail.com>
"""


from __future__ import unicode_literals

############## USER CONFIGURATION START ##############

# Shortcuts need to be single keys on Anki 2.0.x
# Key combinations are supported on Anki 2.1.x

# Shortcut that will reveal the hint fields one by one:
##############  USER CONFIGURATION END  ##############

import json
import time
import shutil
import os
import subprocess
from datetime import timedelta
import platform
operating_system = platform.system()
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from python_mpv_jsonipc import MPV
from pysubs2 import SSAFile
import pysubs2
import datetime
import shutil
import time

# Define a function to switch to English audio track if available
###############

#class DevNull:
#    def write(self, msg):
#        pass
#sys.stderr = DevNull()
###################
noduetoday = 0
script_dir = os.path.dirname(os.path.abspath(__file__))

is_old_fillRev = True




try:
    with open(os.path.abspath(os.path.join(script_dir, "mpvanki.json")), "r") as file:
        data = json.load(file)
    ankivideo = data.get("ankivideo")
except:
    print("Make sure you selected the video folder.")
    try:
        with open(os.path.abspath(os.path.join(script_dir, "mpvanki.json")), "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        # If the file doesn't exist, create an empty dictionary
        data = {}

    # Add or update the object in the dictionary
    data["ankivideo"] = f"{input('videos directory: ')}"

    # Write the updated dictionary to the JSON file
    with open(os.path.abspath(os.path.join(script_dir, "mpvanki.json")), "w") as file:
        json.dump(data, file, indent=4)
    with open(os.path.abspath(os.path.join(script_dir, "mpvanki.json")), "r") as file:
        data = json.load(file)
    ankivideo = data.get("ankivideo")


def jessygo(object_key, object_value):
    # Load the JSON file
    try:
        with open(os.path.abspath(os.path.join(ankivideo, "stamp", "mpvanki.json")), "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        # If the file doesn't exist, create an empty dictionary
        data = {}

    # Add or update the object in the dictionary
    data[object_key] = object_value

    # Write the updated dictionary to the JSON file
    with open(os.path.abspath(os.path.join(ankivideo, "stamp", "mpvanki.json")), "w") as file:
        json.dump(data, file, indent=4)

def jessycome(object_key):
    # Load the JSON file
    try:
        with open(os.path.abspath(os.path.join(ankivideo, "stamp", "mpvanki.json")), "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        # If the file doesn't exist, return None
        return None

    # Return the value of the object
    return data.get(object_key)












def  new_fillRev(self, recursing=False) -> bool:
        try:
            lim = min(self.queueLimit, self._currentRevLimit())
            if lim:
                self._revQueue = self.col.db.list(
                    f"""
    select id from cards where
    did in %s and queue = {QUEUE_TYPE_REV} and due <= ?
    order by nid
    limit ?"""
# order by due, random()
                    % self._deckLimit(),
                    self.today,
                    lim,
                )

                if self._revQueue:
                    # preserve order
                    self._revQueue.reverse()
                    return True
        except: pass

        return False




if operating_system == "Windows":
    windows_dir = os.path.join(script_dir, "windows")
    path = os.environ.get("PATH", "")
    if windows_dir not in path:
        os.environ["PATH"] = windows_dir + os.pathsep + path


def millis_to_time_format(milliseconds):
    milliseconds = int(milliseconds)
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return '{:01d}.{:02d}.{:02d}.{:03d}'.format(hours, minutes, seconds, milliseconds)

def time_format_to_millis(time_format):
    hours, minutes, seconds, milliseconds = map(int, time_format.split('.'))
    total_milliseconds = (hours * 60 * 60 * 1000) + (minutes * 60 * 1000) + (seconds * 1000) + milliseconds
    return total_milliseconds

def remove_overlapping(time_intervals):
    result = []
    for interval in time_intervals:
        if not result or interval[0] >= result[-1][1]:
            result.append(interval)
    return result

def adjust_intervals(time_intervals):
    adjusted_intervals = []
    for interval in time_intervals:
        adjusted_start = max(0, interval[0] - 500)
        adjusted_end = interval[1] + 500
        adjusted_intervals.append((adjusted_start, adjusted_end))
    return adjusted_intervals

def combine_intervals(time_intervals):
    combined_intervals = []
    prev_end = None

    for interval in time_intervals:
        start, end = interval
        if prev_end is not None and prev_end == start and (end - prev_end) <= 2500:
            combined_intervals[-1] = (combined_intervals[-1][0], end)
        else:
            combined_intervals.append(interval)
        prev_end = end

    return combined_intervals


def sort_by_first_timestamp(lst):
    return sorted(lst, key=lambda x: x[0])


def extract_timestamps(file):
    subs = SSAFile.load(file)
    timestamps = []
    added = set()
    start2 = 0
    end2 = 0
    for line in subs:
        start0 = int(line.start)
        end0 = int(line.end)
        start = int(line.start - 500)
        end = int(line.end + 500)
        if start < 0:
            start = 0
        startt = millis_to_time_format(start0)
        endd = millis_to_time_format(end0)
        timestamp = f"{startt} - {endd}"
        if timestamp not in added:
            if end0 - start0 > 100:
                added.add(timestamp)
                end2 = end0
                timestamps.append((f"{startt}", f"{endd}"))
    return timestamps


def assemble(mkve, stampa, track):
    tempy = os.path.join(str(ankivideo),"stamp", "tmp.srt") 
    for file in mkve:
        src_video_paths = []
        filey = str(file)
        file = os.path.join(str(ankivideo), file)
        if file.endswith('mkv'):
            src_video_paths.append(file)
        for src_video_path in src_video_paths:
            os.system(f'mkvextract "{src_video_path}" tracks {track}:"{tempy}"\n')

            new_filepath = src_video_path.replace('.mkv', '.srt')
            shutil.copy(tempy, os.path.join(str(ankivideo),new_filepath))

            subs = pysubs2.load(tempy)
            subs.save(tempy, format="srt")
        timestamps = extract_timestamps(tempy)
        timestamps = sort_by_first_timestamp(timestamps) 
        timestamps = [(time_format_to_millis(start), time_format_to_millis(end)) for start, end in timestamps]
        timestamps = remove_overlapping(timestamps)
        timestamps = adjust_intervals(timestamps)
        timestamps = [(millis_to_time_format(start), millis_to_time_format(end)) for start, end in timestamps]
        os.remove(tempy)
        counter = 0

        with open(os.path.join(str(ankivideo), f'stamp/{os.path.splitext(stampa)[0]}.txt') , 'a') as f:
            for start, end in timestamps:
                counter += 1
                formatted_counter = str(counter).zfill(5)
                f.write(f"new	0	{filey}{formatted_counter}	{filey}	{start}	{end}	{formatted_counter}\n")


def assemble2(mkve, stampa, track):
    for file in mkve:
        src_video_paths = []
        filey = str(file)
        file = os.path.join(str(ankivideo), file)
        base, ext = os.path.splitext(str(file))
        tempy = os.path.join(str(ankivideo), str(file).replace(ext, ".srt")) 
        if file.endswith('mkv'):
            src_video_paths.append(file)
        for src_video_path in src_video_paths:

            subs = pysubs2.load(tempy)
            subs.save(tempy, format="srt")
        timestamps = extract_timestamps(tempy)
        timestamps = sort_by_first_timestamp(timestamps) 
        timestamps = [(time_format_to_millis(start), time_format_to_millis(end)) for start, end in timestamps]
        timestamps = remove_overlapping(timestamps)
        timestamps = adjust_intervals(timestamps)
        timestamps = [(millis_to_time_format(start), millis_to_time_format(end)) for start, end in timestamps]
        counter = 0

        with open(os.path.join(str(ankivideo), f'stamp/{os.path.splitext(stampa)[0]}.txt') , 'a') as f:
            for start, end in timestamps:
                counter += 1
                formatted_counter = str(counter).zfill(5)
                f.write(f"new	0	{filey}{formatted_counter}	{filey}	{start}	{end}	{formatted_counter}\n")

def synclist():
    if not os.path.exists(os.path.abspath(os.path.join(str(jessycome("ankivideo")), "stamp"))):
        os.makedirs(os.path.abspath(os.path.join(str(jessycome("ankivideo")), "stamp")))
    exclude_list = os.listdir(os.path.abspath(os.path.join(str(jessycome("ankivideo")), "stamp")))
    if not exclude_list:
        exclude_list = []
    exclude_list = [f for f in exclude_list if f.endswith('.txt')]
    exclude_list = [os.path.splitext(name)[0] for name in exclude_list]

    all_files = os.listdir(jessycome("ankivideo"))
    result = [f for f in all_files if (os.path.isdir(os.path.join(ankivideo, f)) or f.endswith('.mkv') or f.endswith('.mp4') ) and f != 'stamp']
    result = [os.path.splitext(name)[0] for name in result]
    result = [item for item in result if item not in exclude_list]
    result.sort()
    return result

def filesinside(folder):
    all_files = os.listdir(folder)
    result = [f for f in all_files if f.endswith('.mkv') or f.endswith('.mp4') ]
    result.sort()
    return result

def ofolder(where):
    if platform.system() == "Windows":
        os.startfile(where)
    else:
        os.system('xdg-open "%s" &' % os.path.abspath(os.path.join(str(jessycome("ankivideo")), "stamp")))
    return


def addnewstuff(number=0):
    global sniff
    sniff = []
    global ankivideo
    if not os.path.exists(os.path.abspath(str(jessycome("ankivideo")))):
#         showInfo("Make sure you selected the video folder.")
        print("Make sure you selected the video folder.")
        return
    be = synclist()
    if be != []:
        pass
    else:
        if number == 0:
#             showInfo("There are no new files.")
            print("There are no new files.")
            return

    def my_background_op(be) -> int:
        hay = -1
        for thing in be:
            hay = hay+1
            global track
            print(track[hay])
            if os.path.isdir(os.path.abspath(os.path.join(str(jessycome("ankivideo")), thing))):
                thingss = filesinside(os.path.abspath(os.path.join(str(jessycome("ankivideo")), thing)))
                thingss = [os.path.join(thing, name) for name in thingss]
                print(f"folder {thingss}")
                if track[hay] != "0":
                    assemble(thingss, thing, track[hay])
                else:
                    #test
                    assemble2(thingss, thing, track[hay])
                    #test
            if os.path.isfile(os.path.abspath(os.path.join(str(jessycome("ankivideo")), thing + ".mkv"))):
                thing = thing + ".mkv"
                print(f"file {thing}")
                if track[hay] != "0":
                    assemble([thing], thing, track[hay])
                else:
                    #test
                    assemble2([thing], thing, track[hay])
                    #test
            if os.path.isfile(os.path.abspath(os.path.join(str(jessycome("ankivideo")), thing + ".mp4"))):
                thing = thing + ".mp4"
                print(f"file {thing}")
                if track[hay] != "0":
                    assemble([thing], thing, track[hay])
                else:
                    #test
                    assemble2([thing], thing, track[hay])
                    #test

        return len(be)


    def on_success(count: int) -> None:
        mw.progress.finish()
        if count > 0:
            ofolder(os.path.abspath(os.path.join(str(jessycome("ankivideo")), "stamp")))
#             showInfo("The files are locked and loaded.")
            print("The files are locked and loaded.")
        if sniff != []:
#             showInfo(f"I sniff a non-compatible mkv: {sniff}.")
            print(f"I sniff a non-compatible mkv: {sniff}.")

    global track
    track = []
    for thing in be:
        if os.path.isdir(os.path.abspath(os.path.join(str(jessycome("ankivideo")), thing))):
            thingss = filesinside(os.path.abspath(os.path.join(str(jessycome("ankivideo")), thing)))
            thingss = [os.path.join(thing, name) for name in thingss]
            try:
                command = ['ffprobe', '-v', 'error', '-select_streams', 's', '-show_entries', 'stream=index,codec_name:stream_tags=title,language', '-of', 'default=noprint_wrappers=1', '-print_format', 'csv', os.path.join(str(ankivideo), thingss[0])]
            except:
#                 showWarning("Error: Please ensure that the folders you are adding are not empty and that the files that are not in a folder do not conflict with any existing folder names")
                break
            tete = subprocess.check_output(command).decode()
            try:
                track.append(input(f"{thing}\nselect track:\nType 0 If you are gonna use an external sub file with the same name as the video file \n{tete}")[0])
            except:
#                 showWarning("Error: Please ensure that the folders you are adding are not empty and that the files that are not in a folder do not conflict with any existing folder names")
                break
        if os.path.isfile(os.path.abspath(os.path.join(str(jessycome("ankivideo")), thing + ".mkv"))):
            thing = thing + ".mkv"
            try:
                command = ['ffprobe', '-v', 'error', '-select_streams', 's', '-show_entries', 'stream=index,codec_name:stream_tags=title,language', '-of', 'default=noprint_wrappers=1', '-print_format', 'csv', os.path.join(str(ankivideo), thing)]
            except:
#                 showWarning("Error: Please ensure that the folders you are adding are not empty and that the files that are not in a folder do not conflict with any existing folder names")
                print("Error: Please ensure that the folders you are adding are not empty and that the files that are not in a folder do not conflict with any existing folder names")
                break
            tete = subprocess.check_output(command).decode()
            try:
                track.append(input(f"{thing}\nselect track:\nType 0 If you are gonna use an external sub file with the same name as the video file \n{tete}")[0])
            except:
#                 showWarning("Error: Please ensure that the folders you are adding are not empty and that the files that are not in a folder do not conflict with any existing folder names")
                print("Error: Please ensure that the folders you are adding are not empty and that the files that are not in a folder do not conflict with any existing folder names")
                break
        if os.path.isfile(os.path.abspath(os.path.join(str(jessycome("ankivideo")), thing + ".mp4"))):
            thing = thing + ".mp4"
            try:
                command = ['ffprobe', '-v', 'error', '-select_streams', 's', '-show_entries', 'stream=index,codec_name:stream_tags=title,language', '-of', 'default=noprint_wrappers=1', '-print_format', 'csv', os.path.join(str(ankivideo), thing)]
            except:
#                 showWarning("Error: Please ensure that the folders you are adding are not empty and that the files that are not in a folder do not conflict with any existing folder names")
                print("Error: Please ensure that the folders you are adding are not empty and that the files that are not in a folder do not conflict with any existing folder names")
                break
            tete = subprocess.check_output(command).decode()
            try:
                track.append(input(f"{thing}\nselect track:\nType 0 If you are gonna use an external sub file with the same name as the video file \n{tete}")[0])
            except:
#                 showWarning("Error: Please ensure that the folders you are adding are not empty and that the files that are not in a folder do not conflict with any existing folder names")
                print("Error: Please ensure that the folders you are adding are not empty and that the files that are not in a folder do not conflict with any existing folder names")
                break
    try:
        if track[0]:
            my_background_op(be)
    except:
        print("nothing new")
        pass

progre = []
try:
    subprocess.check_output(['mpv', '--version'])
except:
    progre.append("mpv")
try:
    subprocess.check_output(['ffprobe', '-version'])
except:
    progre.append("ffprobe")
try:
    subprocess.check_output(['mkvextract', '--version'])
except:
    progre.append("mkvextract")
if progre != []:
#         showInfo(f"Next step is to download these programs and set them as environment variables:\n {progre} \n You can use your favorite package manager to do that or just go to these links: \n https://mpv.io/installation/ \n https://ffbinaries.com/downloads \n https://sourceforge.net/projects/gmkvextractgui/")
    print(f"Next step is to download these programs and set them as environment variables:\n {progre} \n You can use your favorite package manager to do that or just go to these links: \n https://mpv.io/installation/ \n https://ffbinaries.com/downloads \n https://sourceforge.net/projects/gmkvextractgui/")
    exit()








def dueToday():
    try:
        global nue
        mpv.command("show-text", str(counterr)) 
    except:
        pass



def espeak():
    os.system("espeak e")

def time_in_seconds(time):
    h, m, s, ms = map(int, time.split('.'))
    total_seconds = (h * 3600) + (m * 60) + s
    return "{}.{}".format(total_seconds, ms)
global stopa
stopa = []
stopan = -1
def mpvankii(v1, v2, v3, v4, v5, v6):
    global noduetoday
    if noduetoday == 0:
        dueToday()
    else:
        noduetoday = 0
    os.path.abspath(os.path.join(ankivideo, v1))
    if not os.path.exists(os.path.abspath(os.path.join(ankivideo, v1))):
        try:
#             tooltip("the files is not in the folder")
            print("the files is not in the folder")
        except:
            pass
        return
    if not v5:
        v5=0
    if not v6:
        v6=0

    START=float(time_in_seconds(v2))
    END=float(time_in_seconds(v3))
    try:
        number = int(str(v4).lstrip("0"))
    except:
        number = int(999)




    global var1,var2,var3,var4,var5
    var1 = jessycome("var1") 
    var2 = str(jessycome("var2")) 
    var3 = str(jessycome("var3"))
    var4 = jessycome("var4") 
    try:
        if v5 == "yes":
            var5 = float(jessycome(str(v1)))
    except:
        jessygo(str(v1),END) 
        var5 = float(jessycome(str(v1)))

    if "1" == v6:
        mpv.command("set_property", "sub-visibility", True)
    else:
        mpv.command("set_property", "sub-visibility", False)

    workingfile=str(mpv.command("get_property", "path"))
    if os.path.abspath(str(workingfile)) != os.path.abspath(os.path.join(ankivideo, v1)):
        mpv.command("loadfile", os.path.abspath(os.path.join(ankivideo, v1)))
        if os.path.isfile(os.path.abspath(os.path.join(ankivideo, v1))):
            while True:
                stream=str(mpv.command("get_property", "stream-pos"))
                try:
                    if int(stream) > 0:
                        break
                except: pass
###

    if var1 == v1 and var4 == number - 1 and float(var3) < START and v5 == "yes": 
        pass
    else:
        if v5 == "yes" and number == 1 and var4 != 1:
            mpv.command("seek", 0, "absolute")
        else:
            if v5 == "yes" and float(var5) < START and var5 != 0.0:
                mpv.command("seek", str(var5), "absolute")
            else:
                mpv.command("seek", str(START), "absolute")

#     if "1" == v6:
# #         mpv.command("set_property", "sub-visibility", True)
#         mpv.command("set", "aid", "0") 
#         mpv.command("cycle", "audio")
#         mpv.command("cycle", "audio")
#     else:
# #         mpv.command("set_property", "sub-visibility", False)
#         mpv.command("set", "aid", "0") 
#         mpv.command("cycle", "audio")
#         mpv.command("cycle", "audio")
#         mpv.command("cycle", "audio")
    mpv.command("set_property", "pause", False)

    
# 2. Update json object
# 3. Write json file

    jessygo("var1",v1) 
    jessygo("var2",START) 
    jessygo("var3",END) 
    jessygo("var4",number) 

    if v5 == "yes":
        jessygo(str(v1),END) 


    global EE
    EE = str(END)



def hola(num):
    global EA
    EA = num

global mb
mb = None

def answercard(ansa):
    global counterr
    global newcards
    if ansa == 3:
#         print('three')
        counterr = counterr - 1 
        if newcards != 0:
            newcards = newcards - 1
            date_obj = datetime.datetime.strptime(morning, '%Y-%m-%d')
            new_date = date_obj + datetime.timedelta(days=int(1))
            new_date_str = new_date.strftime('%Y-%m-%d')
            editinterval(nue - 1, new_date_str, 2)
        else:
            date_obj = datetime.datetime.strptime(datee, '%Y-%m-%d')
            new_date = date_obj + datetime.timedelta(days=int(interfal))
            new_date_str = new_date.strftime('%Y-%m-%d')
            new_interfal = int(interfal) * 2
            editinterval(nue - 1,new_date_str, new_interfal)

        mpv.command("show-text", str(counterr)) 
    if ansa == 1:
#         print('one')
#         print(datee)
#         print(interfal)
        if newcards != 0:
            newcards = newcards - 1
            counterr = counterr - 1 
            date_obj = datetime.datetime.strptime(morning, '%Y-%m-%d')
            new_date = date_obj + datetime.timedelta(days=int(1))
            new_date_str = new_date.strftime('%Y-%m-%d')
            editinterval(nue - 1, new_date_str, 2)
        else:
            new_interfal = max(int(interfal) // 2, 1)
            editinterval(nue - 1, datee, new_interfal)
            mpv.command("show-text", str(counterr)) 
def answere():
    global Break
    global Break2
    global EA
    global neww
    global nues
    global nuedo
    global undoer
    global counterr
    global newcards
    Break = 0
    Break2 = 0
    if EA == 1:
        global ansa
        answercard(ansa)
        Break = 1
        EA = 0
    if EA == 2:
        Break = 1
        Break2 = 1
#         mw.moveToState("deckBrowser")
        EA = 0
    if EA == 3:
        global mb
#         mw.form.actionUndo.trigger()
        if len(nues):
            mpv.command("show-text", "Undo") 
            if neww == "yes":
                if nues[-1][1] != "yes":
                    newcards = newcards + 1
            if neww == "yes":
                if nues[-1][1] != "yes":
                    counterr = counterr + 1 
            elif neww != "yes":
                if nues[-1][1] != 1:
                    counterr = counterr + 1 
            undoer = 1
            Break = 1
        else:
            mpv.command("show-text", "Irreversible") 
#         mw.reviewer.show()
        EA = 0
    if EA == 4:
        try:
#             mw.reviewer.show()
            if neww != "yes":
                counterr = counterr - 1 
            editinterval(nue - 1, "deleted", 0)
            mpv.command("show-text", "Deleted") 
            global deleted
            deleted = "yes"
            Break = 1
        except:
            pass
        EA = 0

def stoopu():
    global EE
    try:
        if str(mpv.command("get_property", "time-pos")) != 'None':
                if 0 <= float(str(mpv.command("get_property", "time-pos"))) - float(EE) <= 0.5:
                    mpv.command("set_property", "pause", True)
                    EE = -1
    except:
        pass

#timer = QTimer()
#timer.timeout.connect(answere)
#timer2 = QTimer()
#timer2.timeout.connect(stoopu)
def run_command_field(num , nw="no"):
    global ansa
    if num != 1 and num != 2:
        ansa = 3

    if nw == "yes":
        new = "yes"
    else:
        new = "no"
        if num == 1:
            ansa = 1


    # Get the current note
    sub = "0"
    if num == 1:
        sub = "1"
#     note = mw.reviewer.card.note()
    # Check if a field called "Command" exists
    global mpv
    try:
        mpv.command("get_property", "stream-pos")
    except:
        mpv = MPV(start_mpv=True, ipc_socket=os.path.abspath("/tmp/mpv-socket"))
#             timer.start(10) # Update every 1 second
#             timer2.start(10) # Update every 1 second
        mpv.bind_key_press("y", lambda: add_time('mpvanki_start', 0))
        mpv.bind_key_press("u", lambda: add_time('mpvanki_start', 1))
        mpv.bind_key_press("o", lambda: add_time('mpvanki_end', 0))
        mpv.bind_key_press("p", lambda: add_time("mpvanki_end", 1))
        mpv.bind_key_press("h", lambda: hola(4))
        mpv.bind_key_press("b", lambda: hola(4))

        mpv.bind_key_press("c", lambda: run_command_field(2))
        mpv.bind_key_press("d", lambda: hola(2))
        mpv.bind_key_press("q", lambda: hola(2))
        mpv.bind_key_press("z", lambda: hola(3))
        mpv.bind_key_press("x", lambda: run_command_field(1))
        mpv.bind_key_press("v",lambda: hola(1))

        mpv.bind_key_press("k", lambda: run_command_field(2))
        mpv.bind_key_press(";", lambda: hola(3))
        mpv.bind_key_press("l", lambda: run_command_field(1))
        mpv.bind_key_press("j",lambda: hola(1))

#         mpv.command("set", "fullscreen", "yes")
        mpv.command("set", "video-align-y", "-1")
        mpv.command("set_property", "sub-visibility", False)

    mpvankii(mpvanki_filename , mpvanki_start , mpvanki_end , mpvanki_number , new, sub)

def donothing(num):
    print("undo or not undo this is the question")
def add_time(time_stringg, nu):
    global noduetoday
    noduetoday = 1
    # Split the time string into hours, minutes, seconds, and milliseconds
    if time_stringg == "mpvanki_start":
        time_string2 = mpvanki_start
    if time_stringg == "mpvanki_end":
        time_string2 = mpvanki_end
    time_parts = time_string2.split('.')
    hours = int(time_parts[0])
    minutes = int(time_parts[1])
    seconds = int(time_parts[2])
    milliseconds = int(time_parts[3])

    
    if time_stringg == "mpvanki_start":
        t2ime_string2 = mpvanki_end
    if time_stringg == "mpvanki_end":
        t2ime_string2 = mpvanki_start
    t2ime_parts = t2ime_string2.split('.')
    h2ours = int(t2ime_parts[0])
    m2inutes = int(t2ime_parts[1])
    s2econds = int(t2ime_parts[2])
    m2illiseconds = int(t2ime_parts[3])

    c2urrent_time = timedelta(hours=h2ours, minutes=m2inutes, seconds=s2econds, milliseconds=m2illiseconds)
    # Create a timedelta object with the current time
    current_time = timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)

    # Add 500 milliseconds to the current time
    if nu == 1: new_time = current_time + timedelta(milliseconds=500)
    else: new_time = current_time - timedelta(milliseconds=500)

    # Format the new time into a string
    new_time_string = "{:01d}.{:02d}.{:02d}.{:03d}".format(new_time.seconds//3600, (new_time.seconds//60)%60, new_time.seconds%60, new_time.microseconds//1000)
    total_seconds = new_time.seconds + new_time.microseconds/1000000
    formatted_time = "{:.3f}".format(total_seconds).replace(".", ".")
        
    total_seconds = c2urrent_time.seconds + c2urrent_time.microseconds/1000000
    f2ormatted_time = "{:.3f}".format(total_seconds).replace(".", ".")

    global mpv
    if time_stringg == "mpvanki_start":
        if float(formatted_time) > float(f2ormatted_time):
            try: 
                mpv.command("show-text", "no can do") 
            except: 
                pass
            return
    if time_stringg == "mpvanki_end":
        if float(formatted_time) < float(f2ormatted_time):
            try: 
                mpv.command("show-text", "no can do") 
            except: 
                pass
            return

    if time_stringg == "mpvanki_start":
        adderstart(nue - 1, new_time_string)
    if time_stringg == "mpvanki_end":
        adderend(nue - 1, new_time_string)
    replace_line(file, nue - 1, lines[nue - 1])
    extract_variables_from_linemini(lines[nue - 1])
    if time_stringg == "mpvanki_start":
        if nu == 1:
            try: 
                mpv.command("show-text","-500ms →-----") 
            except: 
                pass
        else: 
            try: 
                mpv.command("show-text","+500ms ←-----") 
            except: 
                pass
        run_command_field(2)
    if time_stringg == "mpvanki_end":
        if nu == 1:
            try: 
                mpv.command("show-text","+500ms -----→") 
            except: 
                pass
            new_time2 = current_time - timedelta(milliseconds=1000)
        else:
            try: 
                mpv.command("show-text","-500ms -----←") 
            except: 
                pass
            new_time2 = current_time - timedelta(milliseconds=1500)
        new_time_string2 = "{:01d}.{:02d}.{:02d}.{:03d}".format(new_time2.seconds//3600, (new_time2.seconds//60)%60, new_time2.seconds%60, new_time2.microseconds//1000)

        if newcards == 0: new = "no"
        else: new = "yes"
        mpvankii( mpvanki_filename, new_time_string2, mpvanki_end, mpvanki_number, new, 0)


def killmpv():
    global mpv
    try:
        mpv.stop()
        try:
            mpv.terminate()
        except:
            pass
        mpv = None
        timer.stop()
        timer2.stop()
    except:
        pass

# gui_hooks.reviewer_did_show_question.append(run_command_field)
# gui_hooks.reviewer_will_end.append(killmpv)

def extract_variables_from_linemini(line):
        parts = line.split('\t')
        global mpvanki_filename, mpvanki_start, mpvanki_end, mpvanki_number
        global datee, interfal
        datee = parts[0]
        interfal = parts[1]
        mpvanki_filename = parts[3]
        mpvanki_start = parts[4]
        mpvanki_end = parts[5]
        mpvanki_number = parts[6].strip()


def currentintervalmini(line):
        line = line.split('\t')
        global datee, interfal
        datee = line[0]
        interfal = line[1]

def editinterval(linenumber, new_date, new_value):
    with open(file, 'r') as f:
        lines = f.readlines()
        if linenumber > len(lines):
            print("Invalid line number")
            return False
    if new_date:
        lines[linenumber] = new_date + '\t' + str(new_value) + '\t' + '\t'.join(lines[linenumber].split('\t')[2:])
    else:
        lines[linenumber] = lines[linenumber].split('\t')[0] + '\t' + str(new_value) + '\t' + '\t'.join(lines[linenumber].split('\t')[2:])
    with open(file, 'w') as f:
        f.writelines(lines)
    return True

def adderstart(linenumber, new_start):
    global lines
    line = lines[linenumber]
    items = line.split('\t')
    items[4] = new_start
    lines[linenumber] = '\t'.join(items)

def replace_line(filename, line_num, new_line):
    with open(filename, 'r') as f:
        lines = f.readlines()

    lines[line_num] = new_line
    with open(filename, 'w') as f:
        f.writelines(lines)

def adderend(linenumber, new_end):
    global lines
    line = lines[linenumber]
    items = line.split('\t')
    items[5] = new_end
    lines[linenumber] = '\t'.join(items)

def howmany(file):
    counterr = 0
    global morning
    with open(file, 'r') as f:
        lines = []
        for line in f:
            lines.append(line)
            currentintervalmini(line)
            try:
                new_date = datetime.datetime.strptime(datee, '%Y-%m-%d').date()
                today = datetime.datetime.strptime(morning, '%Y-%m-%d').date()
                if new_date <= today:
                    counterr = counterr + 1
            except: pass
    return lines, counterr


def extract_variables_from_line(filename, line_number):
    with open(filename, 'r') as f:
        lines = f.readlines()
        line = lines[line_number - 1]  # line_number is 1-indexed
        parts = line.split('\t')
        global mpvanki_filename, mpvanki_start, mpvanki_end, mpvanki_number
        mpvanki_filename = parts[3]
        mpvanki_start = parts[4]
        mpvanki_end = parts[5]
        mpvanki_number = parts[6].strip()



import os
import argparse

parser = argparse.ArgumentParser(description='A test program.')

parser.add_argument("-n", "--new", help="new cards", type=int)
parser.add_argument("-f", "--file", help="file", type=str)
parser.add_argument("-a", "--add", help="add new items", action='store_true')
parser.add_argument("-d", "--dir", help="select videos directory", action='store_true')

args = parser.parse_args()

if (args.add):
    addnewstuff(1)
    exit()

if (args.dir):
    jessygo("ankivideo", f"{input('videos directory: ')}")
    exit()
if (args.new):
    newcards = args.new
else:
    newcards = 0
if (args.file):
    t = time.localtime()
    current_time = time.strftime("%Y%m%d%H%M%S", t)
    file = os.path.join(str(ankivideo),"stamp", args.file) 
    if not os.path.exists(os.path.abspath(os.path.join(ankivideo, "backup"))):
        os.makedirs(os.path.abspath(os.path.join(ankivideo, "backup")))
    shutil.copyfile(os.path.join(ankivideo,"stamp", args.file), os.path.join(str(ankivideo),"backup", f'{current_time}-{args.file}'))


ansa = 0
global EE
global EA
EE = "none"
EA = 0
undoer = 0
nues = []


morningname = os.path.expanduser('~/.cache/morning')

with open(morningname, 'r') as f:
    line = f.readline().strip()

# Split the line at the space character
morning = line.split()[0]

Break = 0
Break2 = 0

global datee 
global interfal 
global mpvanki_filename 
global mpvanki_start 
global mpvanki_end 
global mpvanki_number 




lines, counterr = howmany(file)
nue = 1
ansa = 3

counterr = counterr + newcards
neww = "yes"
deleted = "no"
while True:
    currentintervalmini(lines[nue - 1])
    if datee == "new":
        extract_variables_from_linemini(lines[nue - 1])
        run_command_field(2, "yes")
        while True:
            time.sleep(0.1)
            stoopu()
            answere()
            if Break == 1: 
                if undoer != 1:
                    nues.append((nue, deleted))
                    if deleted == "yes":
                        deleted == "no"
                break

    if undoer == 1:
        if len(nues):
            nue = nues[-1][0] 
            nues = nues[:-1]
            currentintervalmini(lines[nue - 1])
            editinterval(nue - 1, datee, interfal)
        undoer = 0
    else:
        nue = nue + 1
    ansa = 3
    if Break2 == 1 or newcards == 0: 
        break


nues = []
nue = 0
ansa = 3
lines, counterr = howmany(file)
neww = "no"
while True:
    try:
        currentintervalmini(lines[nue - 1])
        if datee != "new":
            try:
                new_date = datetime.datetime.strptime(datee, '%Y-%m-%d').date()
                today = datetime.datetime.strptime(morning, '%Y-%m-%d').date()
            except:
                new_date = 4
                today = 1
            if new_date <= today:
                extract_variables_from_linemini(lines[nue - 1])
                run_command_field(2)
                while True:
                    time.sleep(0.1)
                    stoopu()
                    answere()
                    if Break == 1: 
                        if undoer != 1:
                            nues.append((nue, ansa))
                        break

        if undoer == 1:
            if len(nues):
                nue = nues[-1][0] 
                nues = nues[:-1]
                currentintervalmini(lines[nue - 1])
                editinterval(nue - 1, datee, interfal)
            undoer = 0
        else:
            nue = nue + 1
        ansa = 3
    except: 
        lines, counterr = howmany(file)
        nue = 0
        mpv.command("show-text", "Newround") 
        nues = []
    if Break2 == 1 or counterr == 0: 
        break

killmpv()
