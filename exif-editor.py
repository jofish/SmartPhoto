#you'll need
#start by making yourtself a nice venv to keep everything in
#python3 -m venv ocr-project
#ok now
#if you don't have homebrew installed, you will need it. 
#then: 
#pip install tesseract
#pip install piexif
#brew install tesseract or if you want non-english brew install tesseract-lang
#brew install exiftool
#and you have to get the textcleaner and the textdeskew packages
#and they require
#imagemagick installed from source with option --with-fftw and there is no good way around this.
#you CANNOT use the brew version. It doesn't work any more that way. Even though there are old web pages saying it does.
#they lie.
#
#to do that
#first check you haven't already done it somehow
#identify -version
#and the last line will look something like
#Delegates (built-in): bzlib freetype heic jng jp2 jpeg lcms ltdl lzma openexr png tiff webp xml zlib
#
#see how fftw isn't there? exactly. so:
#
#first install fftw by going to http://www.fftw.org/fftw2_doc/fftw_6.html
#and follow the instructions.

#then you neeed to get libxml hyperlinked from /usr/install
#which isn't standard after OX Mojave or something
#so do this:
#sudo installer -pkg /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg -target /
#or if you prefer 
#cp /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg ~/Desktop
#and then double-click on that thing on your desktop (which hyperlinks libxml to /usr/install)
#
##then get the source from here https://www.imagemagick.org/script/install-source.php#unix
#tar xvzf imagemagic.tar.gz
#
#then install as recommended, namely:
#
#cd ImageMagick-7.0.9
#./configure --with-modules --enable-shared --with-perl --with-fftw #this is crucial
#make
#sudo make install #becausae it needs administrator privledges for some reason.
#then double check it worked
#identify -version
#and check that last line includes fftw like this:
#Delegates (built-in): bzlib fftw freetype heic jng jp2 jpeg lcms ltdl lzma openexr png tiff webp xml zlib


import glob, piexif, json, pprint, subprocess, os, string
testing=True
path = "/Users/jofishkaye/Dropbox/ocr-flickr-project/"

def addtoexif(whatfile, texttoadd, testing=True, clobber=True):
    #get the old ImageDescription
    if testing: print ("\nfile:",whatfile)
    exifdata = subprocess.getoutput(["/usr/local/bin/exiftool -ImageDescription "+whatfile])
    if len(exifdata)==0: current=""
    else: current = exifdata.split(': ',1)[1].strip()
    if testing: print("current:", current)
    #now we add a new thing to the ImageDescription
    if texttoadd in current: return 0 #don't just keep adding if it's already there.
    if clobber: replacement="jfocr "+texttoadd
    else: replacement = current + " jfocr " + texttoadd
    replacer = subprocess.getoutput(["/usr/local/bin/exiftool -ImageDescription="+replacement+" "+whatfile])
    if testing: print(replacer)

def makeacontrastyfile(whatfile,contrastfile):
    command= path+'textcleaner.sh -g "'+whatfile+'" "'+contrastfile+'"'
    print("command: ",command)
    #back=subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, executable='/bin/bash')
    back=subprocess.getoutput(command)
    print(back)
    return

def deskewfile(whatfile,deskewedfile):
    command= path+'textdeskew.sh "'+whatfile+'" "'+deskewedfile+'"'
    print("command: ",command)
    #back=subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, executable='/bin/bash')
    back=subprocess.getoutput(command)
    print(back)
    return

def extracttextfromfile(whatfile,textfile):
    command = "/usr/local/bin/tesseract "+whatfile+" "+textfile
    #out= subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    out=subprocess.getoutput(command)
    print(out)
    return

#listoffiles = glob.glob(path+'samples/*.gif') + glob.glob(path+'samples/*.png') + glob.glob(path+'moreexamples/*.jpg') + glob.glob(path+'samples/*.jpeg')
listoffiles = glob.glob(path+'newsamples/skewtest.png') 
#listoffiles = [y for x in os.walk("/Users/jkaye/Dropbox/flickrsavr-master/nsid/10476975@N00/2018") for y in glob.glob(os.path.join(x[0], '*.jpg'))]


print(len(listoffiles))

for myfile in listoffiles:
    if "contrasty" in myfile: continue
    if "_original" in myfile: continue
    print("myfile: "+myfile)
    #check to see if the text file for that one exists
    textfile = myfile.rsplit(".",1)[0]
    if os.path.isfile(textfile): 
        print ("textfile exists. Continuing.\n")
        continue #if there's already a textfile, don't generate it again or anything else
 
    contrastfile = myfile.replace(".","-contrasty.")
    if not os.path.isfile(contrastfile): 
        if testing: print("making contrastyfile for "+contrastfile)
        makeacontrastyfile(myfile,contrastfile)

    deskewedfile = contrastfile.replace(".","-deskewed.")
    print(deskewedfile)
    if not os.path.isfile(deskewedfile): 
        if testing: print("making deskewedfile for "+deskewedfile)
        deskewfile(contrastfile,deskewedfile)

    #extracttextfromfile(deskewedfile,textfile)
    #text=open(textfile+".txt").read()
    #' '.join(text.split()) #replace all whitespace with spaces                                  
    #addtoexif(myfile, text, True)
    #if os.path.isfile(myfile+"_original"): os.remove(myfile+"_original") #clean up
    
