#find .pa2 file from SPUD
import datetime
import os
import glob
import time
today = datetime.date.today().strftime("%Y%m%d")
os.chdir("E:/ftp-root/PRDV7/SPAN/Outgoing/target/")
pa2filename = max(glob.iglob('NZX.' + today + '*'), key = os.path.getmtime)
pa2source = "E:/ftp-root/PRDV7/SPAN/Outgoing/target/" + pa2filename
print "Used .pa2 file created today at " + pa2filename[13:15] + ":" + pa2filename[15:17]

#write script to change it to .spn, overrides old scripts
todayspnfolder = "//tsclient/C/SPAN files/" + today + " spn/"
todaypa2folder = "//tsclient/C/SPAN files/" + today + " pa2/"
spn = todayspnfolder + "/NZX." + today + ".spn"
os.chdir("C:/Span4/SPANscript/")
SPANitscript = open("SPANitscript.txt", "w")
SPANitscript.write("Load " + pa2source + "\n" + "Save " + spn)
SPANitscript.close()

#create today's folders to put spn and pa2 into
os.makedirs(todayspnfolder)
os.makedirs(todaypa2folder)

#copy pa2 from SPUD to local drive, rename to NZX.yyyymmdd.s.pa2
pa2dest = todaypa2folder + "NZX." + today + ".s.pa2"
import shutil
shutil.copyfile(pa2source,pa2dest)

#run script
import subprocess
os.chdir("C:/Span4/bin")
subprocess.call(["spanit", "C:/Span4/SPANscript/SPANitscript.txt"])

#zip .pa2 and .spn
spnzip = "//tsclient/C/SPAN files/NZX." + today + ".spn" #+ ".zip"
pa2zip = "//tsclient/C/SPAN files/NZX." + today + ".s.pa2" #+ ".zip"
os.chdir(todayspnfolder)
shutil.make_archive(spnzip,'zip')
os.chdir(todaypa2folder)
shutil.make_archive(pa2zip,'zip')
print "Finished"
