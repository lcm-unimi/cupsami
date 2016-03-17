#!/usr/bin/python
#python local cupsatore
#ask to cups server user's jobs infos
#20110311 giorgio_ruffa
#5 realise

# debuggato da blue (28 Gen 2014): il server non restituiva piu' job-name tra gli attributi,
# ho tolto tutto quello che lo riguardava dallo script

from cups import Connection , getUser , setUser
from datetime import datetime
from sys import exit , argv 
import getopt
from django.utils.encoding import smart_str #senza non riusciva a printare i nomi dei file in unicode


#===================================================

class Colors :
	red = "\033[1;31m"
	blue = "\033[1;34m"
	pink = "\033[1;35m"
	green = "\033[1;32m"
	end = "\033[0m"


class Printer_rec:

	def __init__(self, u_job_date=datetime.now() , \
	u_sheets=0):
		self.job_date 	= u_job_date
		self.job_sheets	= u_sheets

	def __init__(self, job_attr={} ):
		if job_attr == None :
			self.job_date 		= datetime.today()
			self.job_sheets 	= 0
		else :
			if job_attr["time-at-completed"] == None :
				print Colors.red + "Warning: " + "the job " ,\
					 job_attr["job-id"] , " has no time" + Colors.end
				print Colors.red + "Warning:  will be used today date" +\
					 Colors.end
				self.job_date 	= datetime.today()
			else :
				self.job_date 	= datetime.fromtimestamp(job_attr["time-at-completed"])
			self.job_sheets = job_attr["job-media-sheets-completed"]

	def __repr__(self):
		return "date: " + str(self.job_date) 	\
			+ " sheets: " + str(self.job_sheets)



#===================================================

def Usage() :
	print "\nCupsami: tells you how many " + \
		"sheets you have printed in the last 30 days"
	print "\nCupsami: restituisce il numero di pagine" + \
		"stampate negli ultimi 30 giorni"
	print '\nUsage: '+argv[0]+' [flags]'	
	print ' -h\tthis help'
	exit(1)

#===================================================

debug = False
#debug = True

#getopt //tnxs jacopogh
try: params = getopt.getopt(argv[1:],'h')
except getopt.GetoptError:
	print 'Wrong parameter'
	Usage()

#help mode (-h)
if "-h" in str(params[0]): Usage()

#get today
t_today = datetime.today()

#our connection
conn = Connection()

jobs_id = conn.getJobs("all",True).keys()

if len(jobs_id) == 0 :
	print
	print "non hai stampato alcuna pagina questo mese"
	print
	exit(0)

#get job attributes	
jobs_attr = []
for i in jobs_id :
	jobs_attr.append( conn.getJobAttributes(i))

#get printers
printers = conn.getPrinters()

#what we are going to print
printers_records = {}

#initialize the dict
#	it's not the py way but works
for i in printers :
	printers_records[i] = []

#parse our jobs_attr and build records
for i in jobs_attr :
	if debug : print i
	#assign printer
	for j in printers :
		if j in i["job-printer-uri"].split("/") :
			#the job is of printer j
			rec = Printer_rec(i)
			if debug : print rec
			#date controll
			delta = t_today - rec.job_date;
			if delta.days > 30 :
				continue
			printers_records[j].append(rec);


#ok now print "nicely"

total_sheets = 0
print
for i in printers_records.items() : 
	#do not print if no records
	if len(i[1]) == 0 : continue
	print Colors.blue + ("="*60) + Colors.end
	print
	print Colors.green + ( i[0].upper()).center(60) \
		+ Colors.end
	print 
	print Colors.red + "JOBS:\n" + Colors.end
	print Colors.pink + "DATE".ljust(10) +" "*15 \
		+ "SHEETS" + Colors.end
	print
	tot_for_printer = 0
	for j in i[1]:
		print  	str(smart_str(j.job_date)).rjust(20) 			+\
				(" "*5) +\
				str(smart_str(j.job_sheets)).rjust(5)
		tot_for_printer += j.job_sheets
		total_sheets += j.job_sheets
	print Colors.red + "\nTOTAL: "  + str(tot_for_printer) + Colors.end
	print

print Colors.blue + ("="*60) + "\n" + Colors.end
print Colors.red + ("TOTAL SHEETS: " + str(total_sheets)).center(60) + Colors.end
print
print Colors.green + "se notate un bug siete pregati di segnalarlo a: " \
	+ "\tadmin(at)lcm.mi.infn.it" + Colors.end
print
